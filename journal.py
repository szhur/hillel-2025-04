import csv
from pathlib import Path

# ─────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────

STORAGE_FILE_NAME = Path(__file__).parent.parent / "storage/students.csv"

MINIMUM_MARK = 1
MAXIMUM_MARK = 12

# ─────────────────────────────────────────────────────────
# INFRASTRUCTURE
# ─────────────────────────────────────────────────────────

class Repository:
    def __init__(self):
        self.students = self.get_storage()

    def get_storage(self):
        with open(STORAGE_FILE_NAME, "r", newline='') as file:
            reader = csv.DictReader(file, fieldnames=["id", "name", "marks", "info"], delimiter=";")
            next(reader, None)  # skip header
            return list(reader)

    def add_student(self, student: dict):
        # Assign a new ID
        next_id = str(max([int(s["id"]) for s in self.students] + [0]) + 1)
        student["id"] = next_id
        student.setdefault("info", "")

        with open(STORAGE_FILE_NAME, "a", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["id", "name", "marks", "info"], delimiter=";")
            writer.writerow(student)

        self.students.append(student)

    def update_storage(self, students: list[dict]):
        with open(STORAGE_FILE_NAME, "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["id", "name", "marks", "info"], delimiter=";")
            writer.writeheader()
            for student in students:
                writer.writerow(student)


repo = Repository()

def inject_repository(func):
    def inner(*args, **kwargs):
        return func(*args, repo=repo, **kwargs)
    return inner

# ─────────────────────────────────────────────────────────
# DOMAIN (student, users, notification)
# ─────────────────────────────────────────────────────────

class StudentService:
    def __init__(self):
        self.repo = repo

    def add_student(self, student: dict) -> dict | None:
        if not student.get("name") or not student.get("marks"):
            return None

        # Convert marks to string for CSV
        student["marks"] = ",".join(map(str, student["marks"]))
        self.repo.add_student(student)
        return student

    def show_students(self):
        print("=========================\n")
        for student in self.repo.students:
            print(f"{student['id']}. Student {student['name']}\n")
        print("=========================\n")

    def show_student(self, student: dict) -> None:
        print(
            "=========================\n"
            f"Student {student['name']}\n"
            f"Marks: {student['marks']}\n"
            f"Info: {student['info']}\n"
            "=========================\n"
        )

    def update_student(self, id_: int, raw_input: str) -> dict | None:
        parsing_result = raw_input.split(";")
        if len(parsing_result) != 2:
            return None

        new_name, new_info = parsing_result
        for student in self.repo.students:
            if student["id"] == str(id_):
                student["name"] = new_name
                student["info"] = new_info
                self.repo.update_storage(self.repo.students)
                return student

        return None

# ─────────────────────────────────────────────────────────
# OPERATIONAL (APPLICATION) LAYER
# ─────────────────────────────────────────────────────────

def ask_student_payload() -> dict:
    ask_prompt = (
        "Enter student's payload data using text template:\n"
        "John Doe;1,2,3,4,5\n"
        "where 'John Doe' is a full name and [1,2,3,4,5] are marks.\n"
        "The data must be separated by ';'\n> "
    )

    def parse(data) -> dict:
        name, raw_marks = data.split(";")
        return {
            "name": name.strip(),
            "marks": [int(item) for item in raw_marks.replace(" ", "").split(",")],
        }

    user_data: str = input(ask_prompt)
    return parse(user_data)


def student_management_command_handle(command: str):
    service = StudentService()

    if command == "show":
        service.show_students()

    elif command == "add":
        data = ask_student_payload()
        student = service.add_student(data)
        if student is None:
            print("Error adding student")
        else:
            print(f"Student {student['name']} is added")

    elif command == "search":
        student_id = input("Enter student's ID: ").strip()
        for student in repo.students:
            if student["id"] == student_id:
                service.show_student(student)
                return
        print(f"Student {student_id} not found")

    elif command == "delete":
        student_id = input("Enter student's ID to delete: ").strip()
        repo.students = [s for s in repo.students if s["id"] != student_id]
        repo.update_storage(repo.students)
        print(f"Student {student_id} deleted.")

    elif command == "update":
        student_id = input("Enter student's ID to update: ").strip()
        for student in repo.students:
            if student["id"] == student_id:
                service.show_student(student)
                raw_input = input("Enter new 'name;info': ")
                updated = service.update_student(int(student_id), raw_input)
                if updated:
                    print(f"Student {updated['name']} updated.")
                else:
                    print("Failed to update student.")
                return
        print(f"Student {student_id} not found.")

# ─────────────────────────────────────────────────────────
# PRESENTATION LAYER
# ─────────────────────────────────────────────────────────

def handle_user_input():
    OPERATIONAL_COMMANDS = ("quit", "help")
    STUDENT_MANAGEMENT_COMMANDS = ("show", "add", "search", "delete", "update")
    AVAILABLE_COMMANDS = (*OPERATIONAL_COMMANDS, *STUDENT_MANAGEMENT_COMMANDS)

    HELP_MESSAGE = (
        "Welcome to the Journal! Use the menu to interact with the application.\n"
        f"Available commands: {', '.join(AVAILABLE_COMMANDS)}"
    )

    print(HELP_MESSAGE)

    while True:
        command = input("\nSelect command: ").strip().lower()

        if command == "quit":
            print("Thanks for using the Journal application")
            break
        elif command == "help":
            print(HELP_MESSAGE)
        elif command in STUDENT_MANAGEMENT_COMMANDS:
            student_management_command_handle(command)
        else:
            print("Unknown command. Type 'help' to see available commands.")

# ─────────────────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    handle_user_input()