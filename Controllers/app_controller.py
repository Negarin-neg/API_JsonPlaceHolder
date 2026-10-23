import logging
from queue import Empty, Queue
from threading import Thread
from typing import Callable

from Data.api_repository import ApiError
from Services.service import DataError
from UI.main_window import MainWindow


logger = logging.getLogger(__name__)


class AppController:
    def __init__(
        self,
        view: MainWindow,
        load_records: Callable[[str], list[dict]],
    ) -> None:
        self.view = view
        self.root = view.root
        self.load_records = load_records

        self.results = Queue()
        self.loading = False
        self.closed = False
        self.after_id = None

        self.view.on_load = self.load
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._schedule_poll()

    def load(self, resource: str) -> None:
        if self.closed or self.loading:
            return

        self.loading = True
        self.view.set_loading(True)

        worker = Thread(
            target=self._fetch,
            args=(resource,),
            daemon=True,
        )

        try:
            worker.start()
        except RuntimeError:
            logger.exception("Failed to start background worker")
            self.loading = False
            self.view.set_loading(False)
            self.view.show_error("شروع دریافت اطلاعات ممکن نشد.")

    def _fetch(self, resource: str) -> None:
        # This method runs outside the GUI thread.
        try:
            records = self.load_records(resource)
        except (ApiError, DataError, ValueError) as exc:
            self.results.put(("error", resource, str(exc)))
        except Exception:
            logger.exception(
                "Unexpected error loading resource %s",
                resource,
            )
            self.results.put(
                (
                    "error",
                    resource,
                    "خطای غیرمنتظره رخ داد؛ جزئیات در ترمینال ثبت شد.",
                )
            )
        else:
            self.results.put(("success", resource, records))

    def _schedule_poll(self) -> None:
        if not self.closed:
            self.after_id = self.root.after(100, self._poll)

    def _poll(self) -> None:
        self.after_id = None

        if self.closed:
            return

        try:
            kind, resource, payload = self.results.get_nowait()
        except Empty:
            pass
        else:
            self.loading = False
            self.view.set_loading(False)

            if kind == "success":
                self.view.show_records(resource, payload)
            else:
                self.view.show_error(payload)

        self._schedule_poll()

    def close(self) -> None:
        if self.closed:
            return

        self.closed = True

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.view.progress.stop()
        self.root.destroy()
