from typing import Any

import requests


class ApiError(Exception):
    """An expected error while retrieving API data."""


class ApiRepository:
    RESOURCES = {
        "posts",
        "comments",
        "albums",
        "photos",
        "todos",
        "users",
    }

    def __init__(
        self,
        base_url: str = "https://jsonplaceholder.typicode.com",
        timeout: float = 10.0,
    ) -> None:
        if timeout <= 0:
            raise ValueError("Timeout must be positive.")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, endpoint: str) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            with requests.get(url, timeout=self.timeout) as response:
                response.raise_for_status()

                try:
                    return response.json()
                except requests.exceptions.JSONDecodeError as exc:
                    raise ApiError(
                        "پاسخ سرور JSON معتبر نیست."
                    ) from exc

        except requests.exceptions.Timeout as exc:
            raise ApiError(
                "مهلت دریافت پاسخ تمام شد. دوباره تلاش کنید."
            ) from exc

        except requests.exceptions.ConnectionError as exc:
            raise ApiError(
                "ارتباط با سرور برقرار نشد."
            ) from exc

        except requests.exceptions.HTTPError as exc:
            status = (
                exc.response.status_code
                if exc.response is not None
                else "unknown"
            )
            raise ApiError(
                f"سرور خطای HTTP {status} برگرداند."
            ) from exc

        except requests.exceptions.RequestException as exc:
            raise ApiError(
                "ارسال درخواست با مشکل مواجه شد."
            ) from exc

    def get_resource(self, resource: str) -> list[dict[str, Any]]:
        if resource not in self.RESOURCES:
            raise ValueError("Unknown resource.")

        data = self._get(resource)

        if not isinstance(data, list):
            raise ApiError("ساختار پاسخ باید یک فهرست باشد.")

        if not all(isinstance(item, dict) for item in data):
            raise ApiError("ساختار رکوردهای پاسخ معتبر نیست.")

        return data

    def get_user(self, user_id: int) -> dict[str, Any]:
        if type(user_id) is not int or user_id < 1:
            raise ValueError("شناسهٔ کاربر باید عدد صحیح مثبت باشد.")

        data = self._get(f"users/{user_id}")

        if not isinstance(data, dict):
            raise ApiError("ساختار اطلاعات کاربر معتبر نیست.")

        return data

    def get_users(self) -> list[dict[str, Any]]:
        return self.get_resource("users")
