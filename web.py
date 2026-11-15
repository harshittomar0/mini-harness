"""Web tools: DuckDuckGo search and fetching a page as plain text (no API keys)."""

from html.parser import HTMLParser
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

MAX_SEARCH_RESULTS = 5
MAX_FETCH_BYTES = 2_000_000
MAX_FETCH_CHARS = 8000
SKIP_TAGS = {"script", "style", "noscript", "svg", "template"}
BLOCK_TAGS = {
    "p", "div", "br", "li", "tr", "section", "article", "header", "footer",
    "h1", "h2", "h3", "h4", "h5", "h6", "pre", "blockquote", "table", "ul", "ol",
}


class PageTextParser(HTMLParser):
    """Converts an HTML page into readable plain text."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.parts = []
        self.skip_depth = 0
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        elif tag == "title":
            self.in_title = True
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        elif tag == "title":
            self.in_title = False
        elif tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif not self.skip_depth:
            self.parts.append(data)

    def text(self):
        lines = (" ".join(line.split()) for line in "".join(self.parts).splitlines())
        return "\n".join(line for line in lines if line)


class SearchResultParser(HTMLParser):
    """Extracts title, URL, and snippet from DuckDuckGo's HTML results page."""

    def __init__(self):
        super().__init__()
        self.results = []
        self.field = None

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        classes = (attrs.get("class") or "").split()
        if "result__a" in classes:
            self.results.append({"title": "", "url": clean_url(attrs.get("href") or ""), "snippet": ""})
            self.field = "title"
        elif "result__snippet" in classes and self.results:
            self.field = "snippet"

    def handle_endtag(self, tag):
        if tag == "a":
            self.field = None

    def handle_data(self, data):
        if self.field:
            self.results[-1][self.field] += data


def clean_url(href):
    if href.startswith("//"):
        href = "https:" + href
    parsed = urlparse(href)
    # DuckDuckGo sometimes wraps results in a redirect: /l/?uddg=<real url>
    if parsed.path == "/l/" and "uddg" in parse_qs(parsed.query):
        return parse_qs(parsed.query)["uddg"][0]
    return href


def web_search(query):
    if not query.strip():
        raise ValueError("query must not be empty")
    request = Request(
        "https://html.duckduckgo.com/html/",
        data=urlencode({"q": query}).encode("utf-8"),
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urlopen(request, timeout=15) as response:
        page = response.read().decode("utf-8", errors="replace")

    parser = SearchResultParser()
    parser.feed(page)
    results = []
    for result in parser.results:
        if "duckduckgo.com/y.js" in result["url"]:  # sponsored result
            continue
        results.append({key: " ".join(value.split()) for key, value in result.items()})
        if len(results) == MAX_SEARCH_RESULTS:
            break
    return {"results": results}


def fetch_url(url):
    if urlparse(url).scheme not in ("http", "https") or not urlparse(url).netloc:
        raise ValueError("url must be a full http:// or https:// address")
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=15) as response:
        final_url = response.geturl()
        content_type = response.headers.get_content_type()
        charset = response.headers.get_content_charset() or "utf-8"
        body = response.read(MAX_FETCH_BYTES)

    if content_type == "text/html":
        parser = PageTextParser()
        parser.feed(body.decode(charset, errors="replace"))
        title, content = " ".join(parser.title.split()), parser.text()
    elif content_type.startswith("text/") or content_type in ("application/json", "application/xml"):
        title, content = "", body.decode(charset, errors="replace")
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

    result = {"url": final_url, "title": title, "content": content[:MAX_FETCH_CHARS]}
    if len(content) > MAX_FETCH_CHARS:
        result["truncated"] = f"Showing the first {MAX_FETCH_CHARS} of {len(content)} characters"
    return result
