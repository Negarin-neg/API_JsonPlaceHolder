from ttkbootstrap.style import Style, ThemeDefinition


def apply_nord_theme(style: Style) -> None:
    theme = ThemeDefinition(
        name="project_nord_dark",
        themetype="dark",
        colors={
            "primary": "#5E81AC",
            "secondary": "#4C566A",
            "success": "#A3BE8C",
            "info": "#88C0D0",
            "warning": "#EBCB8B",
            "danger": "#BF616A",
            "light": "#ECEFF4",
            "dark": "#2E3440",
            "bg": "#2E3440",
            "fg": "#D8DEE9",
            "selectbg": "#5E81AC",
            "selectfg": "#ECEFF4",
            "border": "#4C566A",
            "inputfg": "#ECEFF4",
            "inputbg": "#3B4252",
            "active": "#434C5E",
        },
    )

    style.register_theme(theme)
    style.theme_use(theme.name)

    style.configure(".", font=("Segoe UI", 10))
    style.configure("TButton", padding=(14, 8))
    style.configure("Treeview", rowheight=34)
    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        padding=(8, 10),
    )
