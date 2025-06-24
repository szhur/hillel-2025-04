import enum

class Role(enum.StrEnum):
    STUDENT = enum.auto()
    TEACHER = enum.auto()

class User:
    def __init__(self, name: str, email: str, role: Role) -> None:
        self.name = name
        self.email = email
        self.role = role

    def send_notification(self, notification):
        print(f"Sending notification to {self.name} <{self.email}>")
        print(notification)
        print("-" * 40)

class Notification:
    def __init__(self, subject: str, message: str, attachment: str = "") -> None:
        self.subject = subject
        self.message = message
        self.attachment = attachment

    def format(self) -> str:
        base = f"Subject: {self.subject}\nMessage: {self.message}"
        if self.attachment:
            base += f"\nAttachment: {self.attachment}"
        return base

    def __str__(self) -> str:
        return self.format()

class StudentNotification(Notification):
    def format(self) -> str:
        base = super().format()
        return f"{base}\nSent via Student Portal"

class TeacherNotification(Notification):
    def format(self) -> str:
        base = super().format()
        return f"{base}\nTeacher's Desk Notification"

def main():
    alice = User("Alice", "alice@student.edu", Role.STUDENT)
    bob = User("Bob", "bob@school.edu", Role.TEACHER)

    notif1 = StudentNotification("Exam Schedule", "The midterm exams will start next Monday.", "exam_schedule.pdf")
    notif2 = TeacherNotification("Meeting Reminder", "Don't forget the staff meeting tomorrow at 10am.")

    alice.send_notification(notif1)
    bob.send_notification(notif2)

if __name__ == "__main__":
    main()