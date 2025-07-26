import datetime


class Content:
    def __init__(self, id: int, path: str, title: str, type: str, description: str,
                 cover_image: str, archived_date: datetime.datetime, tags: list[str]):
        self.id = id
        self.path = path
        self.title = title
        self.type = type
        self.description = description
        self.cover_image = cover_image
        self.archived_date = archived_date
        self.tags = tags
