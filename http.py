import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

class Post:
    def __init__(self, id: int, title: str, body: str):
        self.id = id
        self.title = title
        self.body = body


class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.posts: list[Post] = []

    def add_post(self, post: Post):
        self.posts.append(post)

    def average_title_length(self) -> float:
        if not self.posts:
            return 0.0
        return sum(len(p.title) for p in self.posts) / len(self.posts)

    def average_body_length(self) -> float:
        if not self.posts:
            return 0.0
        return sum(len(p.body) for p in self.posts) / len(self.posts)


class BlogAnalytics:
    def __init__(self):
        self.users: list[User] = []

    def fetch_data(self):
        # fetch all users
        users_resp = requests.get(f"{BASE_URL}/users").json()
        user_dict = {}

        for u in users_resp:
            user = User(id=u["id"], name=u["name"])
            self.users.append(user)
            user_dict[user.id] = user

        # fetch posts for each user
        posts_resp = requests.get(f"{BASE_URL}/posts").json()
        for p in posts_resp:
            post = Post(id=p["id"], title=p["title"], body=p["body"])
            user_dict[p["userId"]].add_post(post)

    def user_with_longest_average_body(self) -> User:
        if not self.users:
            return None
        return max(self.users, key=lambda u: u.average_body_length())

    def users_with_many_long_titles(self) -> list[User]:
        result = []
        for u in self.users:
            long_title_count = sum(1 for p in u.posts if len(p.title) > 40)
            if long_title_count > 5:
                result.append(u)
        return result


# Example usage
if __name__ == "__main__":
    analytics = BlogAnalytics()
    analytics.fetch_data()

    longest_body_user = analytics.user_with_longest_average_body()
    print(f"User with longest average post body: {longest_body_user.name}")

    users_long_titles = analytics.users_with_many_long_titles()
    print("Users with more than 5 long-titled posts:")
    for u in users_long_titles:
        print(f"- {u.name}")
