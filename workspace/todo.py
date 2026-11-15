import json
import sys
from pathlib import Path

TODO_FILE = Path("todos.json")


def load():
    if not TODO_FILE.exists():
        return []
    return json.loads(TODO_FILE.read_text())


def save(todos):
    TODO_FILE.write_text(json.dumps(todos, indent=2))


def main():
    if len(sys.argv) < 2:
        print("Usage: python todo.py add <task> | list | done <number>")
        sys.exit(1)

    command = sys.argv[1]
    todos = load()

    if command == "add":
        task = " ".join(sys.argv[2:])
        todos.append({"task": task, "done": False})
        save(todos)
        print(f"Added: {task}")
    elif command == "list":
        for number, todo in enumerate(todos, start=1):
            mark = "x" if todo["done"] else " "
            print(f"{number}. [{mark}] {todo['task']}")
    elif command == "done":
        number = int(sys.argv[2])
        todos[number]["done"] = True
        save(todos)
        print(f"Completed: {todos[number]['task']}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
