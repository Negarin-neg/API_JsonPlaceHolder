from dataclasses import asdict, fields
from typing import Any, Protocol, get_type_hints

from Models.resources import (
    Address,
    Album,
    Comment,
    Company,
    Geo,
    Photo,
    Post,
    Todo,
    User,
)


class DataError(Exception):
    """API data does not match the expected model."""


class UserDataError(DataError):
    """User data does not match the expected model."""


class RepositoryProtocol(Protocol):
    def get_resource(self, resource: str) -> list[dict[str, Any]]:
        ...

    def get_user(self, user_id: int) -> dict[str, Any]:
        ...


MODEL_CLASSES = {
    "posts": Post,
    "comments": Comment,
    "albums": Album,
    "photos": Photo,
    "todos": Todo,
    "users": User,
}

API_FIELD_NAMES = {
    "user_id": "userId",
    "post_id": "postId",
    "album_id": "albumId",
    "thumbnail_url": "thumbnailUrl",
    "catchphrase": "catchPhrase",
}

NESTED_MODELS = {
    "address": Address,
    "geo": Geo,
    "company": Company,
}


def parse_model(model_class: type, data: dict[str, Any]) -> Any:
    if not isinstance(data, dict):
        raise DataError(
            f"ساختار دادهٔ {model_class.__name__} باید object باشد."
        )

    values = {}
    expected_types = get_type_hints(model_class)

    for field in fields(model_class):
        api_name = API_FIELD_NAMES.get(field.name, field.name)

        if api_name not in data:
            raise DataError(
                f"فیلد {api_name} در {model_class.__name__} موجود نیست."
            )

        value = data[api_name]

        if field.name in NESTED_MODELS:
            value = parse_model(NESTED_MODELS[field.name], value)
        else:
            expected_type = expected_types[field.name]

            if type(value) is not expected_type:
                raise DataError(
                    f"نوع فیلد {api_name} در "
                    f"{model_class.__name__} معتبر نیست."
                )

        values[field.name] = value

    return model_class(**values)


def parse_user(user_data: dict[str, Any]) -> User:
    try:
        return parse_model(User, user_data)
    except DataError as exc:
        raise UserDataError(str(exc)) from exc


class ResourceService:
    def __init__(self, repository: RepositoryProtocol) -> None:
        self.repository = repository

    def get_records(self, resource: str) -> list[dict[str, Any]]:
        if resource not in MODEL_CLASSES:
            raise ValueError("Unknown resource.")

        raw_records = self.repository.get_resource(resource)
        model_class = MODEL_CLASSES[resource]
        records = []

        for index, raw_record in enumerate(raw_records, start=1):
            try:
                model = parse_model(model_class, raw_record)
            except DataError as exc:
                raise DataError(
                    f"رکورد شمارهٔ {index}: {exc}"
                ) from exc

            records.append(asdict(model))

        return records


# Kept for compatibility with the previous console and UsersWindow code.
class UserService:
    def __init__(self, repository: RepositoryProtocol) -> None:
        self.repository = repository

    def get_user(self, user_id: int) -> User:
        return parse_user(self.repository.get_user(user_id))

    def get_users(self) -> list[User]:
        return [
            parse_user(item)
            for item in self.repository.get_resource("users")
        ]
