import json
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

import ttkbootstrap as ttk

from UI.Component.resource_config import (
    RESOURCE_COLUMNS,
    get_cell_value,
)


class MainWindow:
    PAGE_SIZE = 100

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.on_load = lambda resource: None

        self.resource = tk.StringVar(value="users")
        self.search = tk.StringVar()
        self.status = tk.StringVar(value="برای شروع بارگذاری را بزنید.")
        self.page_status = tk.StringVar(value="Page 0 / 0")

        self.loaded_resource = None
        self.records = []
        self.filtered_records = []
        self.search_texts = []
        self.visible_records = {}
        self.page = 0
        self.loading = False

        self.root.title("JSONPlaceholder Explorer")
        self.root.geometry("1180x800")
        self.root.minsize(900, 650)

        self._build_widgets()
        self._configure_columns("users")
        self.search.trace_add("write", self._filter_records)
        self._render_page()

    def _build_widgets(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(3, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        ttk.Label(
            header,
            text="JSONPlaceholder Explorer",
            font=("Segoe UI", 21, "bold"),
            bootstyle="info",
        ).pack(side="left")

        ttk.Label(
            header,
            text="Python • Layered Architecture",
            bootstyle="secondary",
        ).pack(side="right")

        toolbar = ttk.Frame(container)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(toolbar, text="Resource:").pack(
            side="left", padx=(0, 8)
        )

        self.resource_box = ttk.Combobox(
            toolbar,
            textvariable=self.resource,
            values=list(RESOURCE_COLUMNS),
            state="readonly",
            width=16,
            bootstyle="info",
        )
        self.resource_box.pack(side="left", padx=(0, 12))
        self.resource_box.bind(
            "<<ComboboxSelected>>",
            self._resource_changed,
        )

        self.load_button = ttk.Button(
            toolbar,
            text="بارگذاری / تازه‌سازی",
            command=self._request_load,
            bootstyle="success",
            cursor="hand2",
        )
        self.load_button.pack(side="left")

        self.progress = ttk.Progressbar(
            toolbar,
            mode="indeterminate",
            length=150,
            bootstyle="info",
        )
        self.progress.pack(side="right")

        search_bar = ttk.Frame(container)
        search_bar.grid(row=2, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(search_bar, text="Search:").pack(
            side="left", padx=(0, 8)
        )

        ttk.Entry(
            search_bar,
            textvariable=self.search,
            bootstyle="info",
        ).pack(side="left", fill="x", expand=True)

        ttk.Button(
            search_bar,
            text="پاک کردن",
            command=lambda: self.search.set(""),
            bootstyle="secondary-outline",
        ).pack(side="left", padx=(8, 0))

        table_frame = ttk.Frame(container)
        table_frame.grid(row=3, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.table = ttk.Treeview(
            table_frame,
            show="headings",
            selectmode="browse",
            bootstyle="primary",
        )
        self.table.grid(row=0, column=0, sticky="nsew")

        vertical = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.table.yview,
        )
        vertical.grid(row=0, column=1, sticky="ns")

        horizontal = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.table.xview,
        )
        horizontal.grid(row=1, column=0, sticky="ew")

        self.table.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set,
        )
        self.table.tag_configure("even", background="#3B4252")
        self.table.tag_configure("odd", background="#2E3440")
        self.table.bind("<<TreeviewSelect>>", self._show_details)

        pagination = ttk.Frame(container)
        pagination.grid(row=4, column=0, sticky="ew", pady=10)

        self.previous_button = ttk.Button(
            pagination,
            text="Previous",
            command=lambda: self._change_page(-1),
            bootstyle="info-outline",
        )
        self.previous_button.pack(side="left")

        ttk.Label(
            pagination,
            textvariable=self.page_status,
        ).pack(side="left", padx=16)

        self.next_button = ttk.Button(
            pagination,
            text="Next",
            command=lambda: self._change_page(1),
            bootstyle="info-outline",
        )
        self.next_button.pack(side="left")

        details_frame = ttk.LabelFrame(
            container,
            text="جزئیات رکورد انتخاب‌شده",
            padding=10,
            bootstyle="info",
        )
        details_frame.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        self.details = ScrolledText(
            details_frame,
            height=9,
            wrap="word",
            font=("Consolas", 10),
            background="#3B4252",
            foreground="#ECEFF4",
            insertbackground="#ECEFF4",
            selectbackground="#5E81AC",
            selectforeground="#ECEFF4",
            relief="flat",
            padx=10,
            pady=10,
        )
        self.details.pack(fill="both", expand=True)
        self.details.configure(state="disabled")

        ttk.Label(
            container,
            textvariable=self.status,
            anchor="w",
            wraplength=850,
        ).grid(row=6, column=0, sticky="ew")

    def _request_load(self) -> None:
        if not self.loading:
            self.on_load(self.resource.get())

    def _resource_changed(self, _event=None) -> None:
        if not self.loading:
            self._clear_records()
            self._configure_columns(self.resource.get())
            self._request_load()

    def _configure_columns(self, resource: str) -> None:
        columns = RESOURCE_COLUMNS[resource]
        names = [name for name, _, _ in columns]

        self.table.configure(
            columns=names,
            displaycolumns=names,
        )

        for name, title, width in columns:
            self.table.heading(name, text=title)
            self.table.column(
                name,
                width=width,
                minwidth=60,
                stretch=name not in ("id", "user_id", "post_id", "album_id"),
            )

    def _clear_records(self) -> None:
        self.records = []
        self.filtered_records = []
        self.search_texts = []
        self.loaded_resource = None
        self.page = 0
        self.search.set("")
        self._render_page()

    def set_loading(self, loading: bool) -> None:
        self.loading = loading
        self.load_button.configure(
            state="disabled" if loading else "normal"
        )
        self.resource_box.configure(
            state="disabled" if loading else "readonly"
        )

        if loading:
            self.status.set("در حال دریافت اطلاعات...")
            self.progress.start(10)
        else:
            self.progress.stop()

    def show_records(self, resource: str, records: list[dict]) -> None:
        self.loaded_resource = resource
        self.records = records
        self.search_texts = [
            json.dumps(record, ensure_ascii=False).casefold()
            for record in records
        ]
        self._configure_columns(resource)
        self._filter_records()

    def _filter_records(self, *_args) -> None:
        query = self.search.get().strip().casefold()

        self.filtered_records = [
            record
            for record, text in zip(self.records, self.search_texts)
            if not query or query in text
        ]

        self.page = 0
        self._render_page()

    def _render_page(self) -> None:
        self.visible_records.clear()

        for item_id in self.table.get_children():
            self.table.delete(item_id)

        self._set_details("برای نمایش جزئیات، یک ردیف را انتخاب کنید.")

        resource = self.loaded_resource or self.resource.get()
        columns = RESOURCE_COLUMNS[resource]
        start = self.page * self.PAGE_SIZE
        page_records = self.filtered_records[
            start:start + self.PAGE_SIZE
        ]

        for index, record in enumerate(page_records):
            item_id = self.table.insert(
                "",
                "end",
                values=[
                    get_cell_value(record, name)
                    for name, _, _ in columns
                ],
                tags=("even" if index % 2 == 0 else "odd",),
            )
            self.visible_records[item_id] = record

        total = len(self.filtered_records)
        page_count = (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        current = self.page + 1 if total else 0

        self.page_status.set(f"Page {current} / {page_count}")

        self.previous_button.configure(
            state="normal" if self.page > 0 else "disabled"
        )
        self.next_button.configure(
            state=(
                "normal"
                if self.page + 1 < page_count
                else "disabled"
            )
        )

        if not self.loading:
            if self.loaded_resource is None:
                self.status.set("هنوز اطلاعاتی بارگذاری نشده است.")
            else:
                self.status.set(
                    f"{resource} | کل رکوردها: {len(self.records)}"
                    f" | نتیجهٔ جست‌وجو: {total}"
                    f" | نمایش در این صفحه: {len(page_records)}"
                )

    def _change_page(self, direction: int) -> None:
        page_count = (
            len(self.filtered_records) + self.PAGE_SIZE - 1
        ) // self.PAGE_SIZE

        new_page = self.page + direction

        if 0 <= new_page < page_count:
            self.page = new_page
            self._render_page()

    def _set_details(self, text: str) -> None:
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", text)
        self.details.configure(state="disabled")

    def _show_details(self, _event=None) -> None:
        selected = self.table.selection()

        if not selected:
            return

        record = self.visible_records.get(selected[0])

        if record is not None:
            self._set_details(
                json.dumps(record, ensure_ascii=False, indent=2)
            )

    def show_error(self, message: str) -> None:
        self.status.set(
            "دریافت ناموفق بود؛ دادهٔ قبلی، در صورت وجود، حفظ شده است."
        )
        messagebox.showerror(
            "خطا",
            message,
            parent=self.root,
        )
