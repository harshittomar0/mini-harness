import json
from urllib.error import URLError
from urllib.request import Request, urlopen

import skills
import tools

LLM_URL = "http://127.0.0.1:8000/chat/" 


def tools_prompt(tool_list, guidance):
    """tool_list holds (name, description, example args) for every tool the model may call."""
    examples = [
        json.dumps({"tool": name, "args": args}) + f"  # {description}"
        for name, description, args in tool_list
    ]
    return (
        "To use a tool, reply ONLY with a JSON object in one of these formats:\n"
        + "\n".join(examples)
        + f"\n{guidance}"
        + f"\nWorkspace folder: {tools.WORKSPACE_ROOT}"
        + "\nAfter a tool result, request another tool or answer with plain text."
    )

def ask_llm(conversation):
    request = Request(
        LLM_URL,
        data=json.dumps({"message": "\n".join(conversation)}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:
        data = json.load(response)
    if not isinstance(data, dict) or not isinstance(data.get("message"), str):
        raise ValueError("Server response must contain a message string")
    return data["message"]


def chat(prompt, call_tool):
    """Outer loop reads user input; inner loop calls the LLM and runs tools until it answers in text."""
    conversation = [prompt]
    while True:
        try:
            message = input("You (exit to quit): ").strip()
            if message.lower() == "exit":
                break
            if not message:
                continue

            # #  LOOP
            while True:
                reply = ask_llm(conversation + [f"user: {message}"])
                conversation += [f"user: {message}", f"reply: {reply}"]

                call = json.loads(reply) if reply.lstrip().startswith("{") else None

                # IF NO TOOL or SKILL
                if not isinstance(call, dict) or "tool" not in call:
                    print(f"LLM: {reply}")
                    break

                result = call_tool(call["tool"], call.get("args"))
                message = "Tool result: " + json.dumps(result)
                print(message)
        except URLError as error:
            print(f"Connection error: {error.reason}. Is the LLM server running?")
        except ValueError as error:
            print(f"Invalid tool JSON: {error}")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


def main():
    prompt = "General coding agent."
    tool_list = [(name, tool["description"], tool["args"]) for name, tool in tools.TOOLS.items()]
    tool_text = tools_prompt(tool_list, tools.GUIDANCE)
    skill_text = skills.discover_skills(tools.WORKSPACE_ROOT)

    prompt += "\n" + tool_text + "\n" + skill_text
    print(f"Workspace: {tools.WORKSPACE_ROOT}")
    print(f"Skills catalog: {'skills.md' if skill_text else 'none'}")

    chat(prompt, tools.run_tool)


if __name__ == "__main__":
    main()
