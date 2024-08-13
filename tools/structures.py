from json import loads


class Account:
    def __init__(self, ID: int, nickname: str, login: str, password: str, url: str, icon: str) -> None:
        self.ID: int = ID
        self.nickname: str = nickname
        self.login: str = login
        self.password: str = password
        self.url: str = url
        self.icon: str = icon


class Content:
    def __init__(self, ID: int, filename: str, description: str, datetime: str, likes: int, dislikes: int) -> None:
        self.ID: int = ID
        self.filename: str = filename
        self.description: str = description
        self.datetime: str = datetime
        self.likes: int = likes
        self.dislikes: int = dislikes


class Post:
    def __init__(self, ID: int, ID_user: int, title: str, content: str, comments: int, views: int, url: str, datetime: str) -> None:
        self.ID = ID
        self.ID_user = ID_user
        self.title = title
        self.icon = ''
        self.content = loads(content)
        self.reputation = 0
        self.comments: int = comments
        self.views = views
        self.url = url
        self.datetime = datetime


class Comment:
    def __init__(self, ID: int, ID_user: int, ID_post: int, text: str, datetime: str) -> None:
        self.ID = ID
        self.ID_user = ID_user
        self.ID_post = ID_post
        self.text = text
        self.datetime = datetime
