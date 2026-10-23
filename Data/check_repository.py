from Data.api_repository import ApiError, ApiRepository


def main() -> None:
    repository = ApiRepository()

    try:
        user = repository.get_user(1)
        print("Single user:")
        print(user)

        users = repository.get_users()
        print(f"\nNumber of users: {len(users)}")

        for item in users[:3]:
            print(item.get("id"), item.get("name"))

    except ApiError as exc:
        print(f"API error: {exc}")
    except ValueError as exc:
        print(f"Invalid input: {exc}")


if __name__ == "__main__":
    main()
