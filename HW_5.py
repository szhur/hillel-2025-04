from functools import wraps

users = [
    {"username": "john", "password": "john123"},
    {"username": "alice", "password": "alice456"},
    {"username": "bob", "password": "qwerty"},
]

authenticated = {"user": None}

def auth(func=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if authenticated["user"] is None:
            print("🔐 Authorization required.")
            while True:
                username = input("Username: ").strip()
                password = input("Password: ").strip()
                for user in users:
                    if user["username"] == username and user["password"] == password:
                        authenticated["user"] = user
                        print(f"Welcome, {username}!")
                        break
                else:
                    print("Invalid credentials. Try again.\n")
                    continue
                break
        return func(*args, **kwargs)
    return wrapper

@auth
def command(payload):
    print(f"Executing command by authorized user.\nPayload: {payload}")

while user_input := input("Enter anything: "):
    command(user_input)
