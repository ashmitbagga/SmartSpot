"""Dashboard: live statistics."""
import tkinter as tk
from gui.theme import BG, PANEL, TEXT, MUTED, ACCENT, AVAIL, OCCU, RES, EVCHA, UNAVAIL


class DashboardPage(tk.Frame):
    CARDS = [("total", "Total Spaces", ACCENT), ("available", "Available", AVAIL), ("occupied", "Occupied", OCCU),
             ("reserved", "Reserved", RES), ("ev", "EV Charging Spaces", EVCHA),
             ("unavailable", "Unavailable", UNAVAIL), ("occupancy", "Occupancy %", ACCENT)]

    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        tk.Label(self, text="Dashboard", bg=BG, fg=TEXT, font=("Segoe UI", 20, "bold")).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 15))
        self.values = {}
        for i, (key, title, colour) in enumerate(self.CARDS):
            card = tk.Frame(self, bg=PANEL, highlightbackground=colour, highlightthickness=2, padx=20, pady=15)
            card.grid(row=1 + i // 4, column=i % 4, padx=8, pady=8, sticky="nsew")
            tk.Label(card, text=title,font=("Arial",10),bg=PANEL, fg="white").pack()
            self.values[key] = tk.Label(card, text="0", bg=PANEL, fg=colour, font=("Segoe UI", 26, "bold"))
            self.values[key].pack()
        for c in range(4):
            self.columnconfigure(c, weight=1)

    def refresh(self):
        stats = self.app.parking.get_stats()
        for key, label in self.values.items():
            label.config(text=f"{stats[key]}%" if key == "occupancy" else str(stats[key]))
