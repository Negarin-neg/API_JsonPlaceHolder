RESOURCE_COLUMNS = {
    "users": (
        ("id", "ID", 65),
        ("name", "Name", 220),
        ("email", "Email", 260),
        ("address.city", "City", 180),
    ),
    "posts": (
        ("id", "ID", 65),
        ("user_id", "User ID", 90),
        ("title", "Title", 600),
    ),
    "comments": (
        ("id", "ID", 65),
        ("post_id", "Post ID", 90),
        ("name", "Name", 350),
        ("email", "Email", 260),
    ),
    "albums": (
        ("id", "ID", 65),
        ("user_id", "User ID", 90),
        ("title", "Title", 600),
    ),
    "photos": (
        ("id", "ID", 65),
        ("album_id", "Album ID", 90),
        ("title", "Title", 420),
        ("url", "Image URL", 300),
    ),
    "todos": (
        ("id", "ID", 65),
        ("user_id", "User ID", 90),
        ("title", "Title", 500),
        ("completed", "Completed", 120),
    ),
}


def get_cell_value(record: dict, path: str):
    value = record

    for part in path.split("."):
        if not isinstance(value, dict):
            return ""

        value = value.get(part, "")

    if isinstance(value, bool):
        return "Yes" if value else "No"

    return value
