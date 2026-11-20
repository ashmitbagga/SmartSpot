"""Colours and ttk styling shared by all pages."""
from tkinter import ttk

BG, PANEL, TEXT, MUTED, ACCENT = "#171717", "#262626", "#FAFAFA", "#A3A3A3", "#F97316"
AVAIL,OCCU,RES,EVCHA,ACCESS,UNAVAIL="#f96f20", "#ff0a19", "#AB03A9", "#005af5", "#f6cf23", "#f89f21"
FONT = ("Segoe UI", 10)


def setup_style(root):
    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TCombobox", fieldbackground=PANEL, background=PANEL, foreground=TEXT, arrowcolor=TEXT)
    style.map("TCombobox", fieldbackground=[("readonly", PANEL)], foreground=[("readonly", TEXT)])
    style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT)
    style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=24, borderwidth=0)
    style.configure("Treeview.Heading", background=ACCENT, foreground="white", font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", ACCENT)])
    root.option_add("*TCombobox*Listbox.background", PANEL)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
