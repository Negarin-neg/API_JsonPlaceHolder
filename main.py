import logging

import ttkbootstrap as ttk

from Controllers.app_controller import AppController
from Data.api_repository import ApiRepository
from Services.service import ResourceService
from UI.Component.theme import apply_nord_theme
from UI.main_window import MainWindow


def main() -> None:
    repository = ApiRepository()
    service = ResourceService(repository)

    root = ttk.Window(themename="darkly")
    apply_nord_theme(root.style)

    view = MainWindow(root)
    controller = AppController(
        view=view,
        load_records=service.get_records,
    )

    root.after(0, lambda: controller.load("users"))
    root.mainloop()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    main()
