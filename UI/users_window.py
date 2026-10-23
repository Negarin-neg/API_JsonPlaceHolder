import logging
import tkinter as tk
from queue import Empty, Queue
from threading import Thread
from tkinter import messagebox
import ttkbootstrap as ttk

from typing import Callable

from Data.api_repository import ApiError
from Models.resources import User
from Services.service import UserDataError


logger = logging.getLogger(__name__)


class UsersWindow:
    def __init__(
        self,
        root: tk.Tk,
        load_users: Callable[[], list[User]],
    ) -> None:
        self.root = root
        self.load_users = load_users
        self.users: dict[str, User] = {}
        self.results: Queue = Queue()
        self.loading = False
        self.closed = False

        self.root.title("JSONPlaceholder — Users")
        self.root.geometry("1100x720")
        self.root.minsize(850, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        self.status = tk.StringVar(
            value="برای دریافت کاربران، دکمهٔ بارگذاری را بزنید."
        )
        self.details = tk.StringVar(
            value="برای نمایش جزئیات، یک کاربر را انتخاب کنید."
        )

        self._build_widgets()
        self.root.after(100, self._poll_results)

    def _build_widgets(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(container)
        toolbar.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 12),
        )

        ttk.Label(
            toolbar,
            text="JSONPlaceholder",
            font=("Segoe UI", 20, "bold"),
            bootstyle="info",
        ).pack(side="left", padx=(0, 20))

        self.load_button = ttk.Button(
            toolbar,
            text="بارگذاری / تازه‌سازی",
            command=self._start_loading,
            bootstyle="success",
            cursor="hand2",
        )
        self.load_button.pack(side="left", padx=6)

        ttk.Button(
            toolbar,
            text="خروج",
            command=self._close,
            bootstyle="danger-outline",
            cursor="hand2",
        ).pack(side="right", padx=(12, 0))

        self.progress = ttk.Progressbar(
            toolbar,
            mode="indeterminate",
            length=140,
            bootstyle="info",
        )
        self.progress.pack(side="right")

        table_frame = ttk.Frame(container)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("id", "name", "email", "city")
        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        headings = {
            "id": ("ID", 60),
            "name": ("Name", 220),
            "email": ("Email", 250),
            "city": ("City", 180),
        }

        for column, (title, width) in headings.items():
            self.table.heading(column, text=title)
            self.table.column(column, width=width, minwidth=60)

        vertical = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview,
        )
        horizontal = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.table.xview,
        )

        self.table.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )
        self.table.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        self.table.bind("<<TreeviewSelect>>", self._show_details)

        detail_frame = ttk.LabelFrame(
            container,
            text="جزئیات کاربر",
            padding=10,
        )
        detail_frame.grid(row=2, column=0, sticky="ew", pady=10)

        ttk.Label(
            detail_frame,
            textvariable=self.details,
            justify="left",
            wraplength=620,
        ).pack(anchor="w")

        ttk.Label(
            container,
            textvariable=self.status,
            anchor="w",
        ).grid(row=3, column=0, sticky="ew")

    def _start_loading(self) -> None:
        if self.loading:
            return

        self.loading = True
        self.load_button.state(["disabled"])
        self.status.set("در حال دریافت کاربران...")
        self.progress.start(10)

        Thread(target=self._fetch_users, daemon=True).start()

    def _fetch_users(self) -> None:
        # Worker thread: never access Tkinter widgets here.
        try:
            users = self.load_users()
        except (ApiError, UserDataError) as exc:
            self.results.put(("error", str(exc)))
        except Exception:
            logger.exception("Unexpected error while loading users")
            self.results.put(
                ("error", "خطای غیرمنتظره رخ داد؛ جزئیات در ترمینال ثبت شد.")
            )
        else:
            self.results.put(("success", users))

    def _poll_results(self) -> None:
        if self.closed:
            return

        try:
            kind, payload = self.results.get_nowait()
        except Empty:
            pass
        else:
            self.loading = False
            self.progress.stop()
            self.load_button.state(["!disabled"])

            if kind == "success":
                self._display_users(payload)
            else:
                self.status.set(
                    "دریافت ناموفق بود؛ اطلاعات قبلی، اگر موجود باشد، حفظ شد."
                )
                messagebox.showerror(
                    "خطای دریافت اطلاعات",
                    payload,
                    parent=self.root,
                )

        if not self.closed:
            self.root.after(100, self._poll_results)

    def _display_users(self, users: list[User]) -> None:
        for item_id in self.table.get_children():
            self.table.delete(item_id)

        self.users.clear()
        self.details.set("برای نمایش جزئیات، یک کاربر را انتخاب کنید.")

        for user in users:
            item_id = self.table.insert(
                "",
                "end",
                values=(
                    user.id,
                    user.name,
                    user.email,
                    user.address.city,
                ),
            )
            self.users[item_id] = user

        if users:
            self.status.set(f"{len(users)} کاربر دریافت شد.")
        else:
            self.status.set("هیچ کاربری یافت نشد.")

    def _show_details(self, _event=None) -> None:
        selection = self.table.selection()
        if not selection:
            return

        user = self.users.get(selection[0])
        if user is None:
            return

        self.details.set(
            f"Name: {user.name}\n"
            f"Username: {user.username}\n"
            f"Email: {user.email}\n"
            f"Phone: {user.phone}\n"
            f"Website: {user.website}\n"
            f"Address: {user.address.city}, {user.address.street}, "
            f"{user.address.suite}\n"
            f"Company: {user.company.name}"
        )

    def _close(self) -> None:
        self.closed = True
        self.progress.stop()
        self.root.destroy()
