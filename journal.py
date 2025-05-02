# ─────────────────────────────────────────────────────────
# STORAGE SIMULATION
# ─────────────────────────────────────────────────────────
storage: dict[int, dict] = {
    1: {
        "name": "Alice Johnson",
        "marks": [7, 8, 9, 10, 6, 7, 8],
        "info": "Alice Johnson is 18 y.o. Interests: math",
    },
    2: {
        "name": "Michael Smith",
        "marks": [6, 5, 7, 8, 7, 9, 10],
        "info": "Michael Smith is 19 y.o. Interests: science",
    },
    3: {
        "name": "Emily Davis",
        "marks": [9, 8, 8, 7, 6, 7, 7],
        "info": "Emily Davis is 17 y.o. Interests: literature",
    },
    4: {
        "name": "James Wilson",
        "marks": [5, 6, 7, 8, 9, 10, 11],
        "info": "James Wilson is 20 y.o. Interests: sports",
    },
    5: {
        "name": "Olivia Martinez",
        "marks": [10, 9, 8, 7, 6, 5, 4],
        "info": "Olivia Martinez is 18 y.o. Interests: art",
    },
    6: {
        "name": "Emily Davis",
        "marks": [4, 5, 6, 7, 8, 9, 10],
        "info": "Daniel Brown is 19 y.o. Interests: music",
    },
    7: {
        "name": "Sophia Taylor",
        "marks": [11, 10, 9, 8, 7, 6, 5],
        "info": "Sophia Taylor is 20 y.o. Interests: physics",
    },
    8: {
        "name": "William Anderson",
        "marks": [7, 7, 7, 7, 7, 7, 7],
        "info": "William Anderson is 18 y.o. Interests: chemistry",
    },
    9: {
        "name": "Isabella Thomas",
        "marks": [8, 8, 8, 8, 8, 8, 8],
        "info": "Isabella Thomas is 19 y.o. Interests: biology",
    },
    10: {
        "name": "Benjamin Jackson",
        "marks": [9, 9, 9, 9, 9, 9, 9],
        "info": "Benjamin Jackson is 20 y.o. Interests: history",
    },
}

# ─────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────
MINIMUM_MARK = 1
MAXIMUM_MARK = 12

# ─────────────────────────────────────────────────────────
# CRUD
# ─────────────────────────────────────────────────────────
def add_student(student: dict) -> dict | None:
    if len(student) != 2:
        return None

    if not student.get("name") or not student.get("marks"):
        return None
    else:
        # action
        next_id = max(storage.keys())
        storage[next_id] = student
        return student

def add_mark(student_id : int, raw_mark : str) -> dict | None:
    
    if not raw_mark.isnumeric():
        print("Mark must be a number from 1 to 12!")
        return None
    
    mark = int(raw_mark)
    if mark < MINIMUM_MARK or mark > MAXIMUM_MARK:
        print("Mark must be a number from 1 to 12!")
        return None
    
    student: dict | None = storage.get(student_id)
    if student is None:
        return None
    
    student["marks"].append(int(raw_mark))

    return student


def show_students():
    print("=========================\n")
    for id_, student in storage.items():
        print(f"{id_}. Student {student['name']}\n")
    print("=========================\n")


def show_student(student: dict) -> None:
    print(
        "=========================\n"
        f"Student {student['name']}\n"
        f"Marks: {student['marks']}\n"
        f"Info: {student['info']}\n"
        "=========================\n"
    )


def update_student(id_: int, raw_input: str) -> dict | None:
    parsing_result = raw_input.split(";")
    if len(parsing_result) != 2:
        return None

    new_name, new_info = parsing_result

    student: dict | None = storage.get(id_)
    if student is None:
        return None

    student["name"] = new_name
    student["info"] = new_info

    return student


# ─────────────────────────────────────────────────────────
# OPERATIONAL LAYER
# ─────────────────────────────────────────────────────────
def ask_student_payload() -> dict:
    ask_prompt = (
        "Enter student's payload data using text template: "
        "John Doe;1,2,3,4,5\n"
        "where 'John Doe' is a full name and [1,2,3,4,5] are marks.\n"
        "The data must be separated by ';'"
    )

    def parse(data) -> dict:
        name, raw_marks = data.split(";")

        return {
            "name": name,
            "marks": [int(item) for item in raw_marks.replace(" ", "").split(",")],
        }

    user_data: str = input(ask_prompt)
    return parse(user_data)


def student_management_command_handle(command: str):
    if command == "show":
        show_students()
    elif command == "add":
        data = ask_student_payload()
        if data:
            student: dict | None = add_student(data)
            if student is None:
                print("Error adding student")
            else:
                print(f"Student: {student['name']} is added")
        else:
            print("The student's data is NOT correct. Please try again")
    elif command == "search":
        student_id: str = input("\nEnter student's ID: ")
        if not student_id:
            print("Student's ID is required to search")
            return

        student: dict | None = storage.get(int(student_id))
        if student is None:
            print("Error adding student")
        else:
            show_student(student)
            print(f"Student {student_id} not found")
    elif command == "delete":
        student_id: str = input("\nEnter student's ID: ")
        if not student_id:
            print("Student's id is required to delete")
            return

        id_ = int(student_id)
        if storage.get(id_):
            del storage[id_]

    elif command == "update":
        student_id: str = input("\nEnter student's ID: ")
        if not student_id:
            print("Student ID must be specified for update")
            return

        id_ = int(student_id)
        student: dict | None = storage.get(id_)
        if student is None:
            print(f"Student {student_id} not found")
            return

        show_student(student)
        print(
            f"\n\nTo update user's data, specify `name` and `info`, with `;` separator.\n"
        )

        user_input: str = input("Enter: ")
        updated_student: dict | None = update_student(id_=id_, raw_input=user_input)

        if updated_student is None:
            print("Erorr on updating student")
        else:
            print(f"Student {updated_student['name']} is updated")
    elif command == "add_mark":
        student_id: str = input("\nEnter student's ID: ")
        if not student_id:
            print("Student ID must be specified for update")
            return

        id_ = int(student_id)
        student: dict | None = storage.get(id_)
        if student is None:
            print(f"Student {student_id} not found")
            return

        show_student(student)

        raw_mark: str = input("Enter student's mark: ")
        updated_student: dict | None = add_mark(student_id=id_, raw_mark=raw_mark)

        if updated_student is None:
            print("Erorr on adding mark")
        else:
            print(f"Mark is successfully added")


def handle_user_input():
    OPERATIONAL_COMMANDS = ("quit", "help")
    STUDENT_MANAGEMENT_COMMANDS = ("show", "add", "search", "delete", "update", "add_mark")
    AVAILABLE_COMMANDS = (*OPERATIONAL_COMMANDS, *STUDENT_MANAGEMENT_COMMANDS)

    HELP_MESSAGE = (
        "Hello in the Journal! User the menu to interact with the application.\n"
        f"Available commands: {AVAILABLE_COMMANDS}"
    )

    print(HELP_MESSAGE)

    while True:
        command = input("\n Select command: ")

        if command == "quit":
            print("\nThanks for using the Journal application")
            break
        elif command == "help":
            print(HELP_MESSAGE)
        else:
            student_management_command_handle(command)


# ─────────────────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    handle_user_input()