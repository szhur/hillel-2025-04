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
        # TODO: print out or log the notification
        pass

class Notification:
    def __init__(self, subject: str, message: str, attachment: str = "") -> None:
        self.subject = subject
        self.message = message
        self.attachment = attachment  # Optional extra info

    def format(self) -> str:
        # TODO: implement basic notification formatting
        # TODO: think about `__str__` usage instead of `format`
        pass

class StudentNotification(Notification):
    def format(self) -> str:
        # TODO: add "Sent via Student Portal" to the message
        pass

class TeacherNotification(Notification):
    def format(self) -> str:
        # TODO: add "Teacher's Desk Notification" to the message
        pass

def main():
    # TODO: create users of both types
    # TODO: create notifications
    # TODO: have users print (aka send) their notifications
    pass

if __name__ == "__main__":
    main()