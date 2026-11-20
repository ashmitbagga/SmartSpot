"""Parking Layout page: clickable grid on the left, details/actions panel on the right."""
import tkinter as tk
from tkinter import ttk, messagebox
from gui.theme import BG, PANEL, TEXT, MUTED, ACCENT, AVAIL, OCCU, RES, EVCHA, ACCESS, UNAVAIL
from gui.vehicle_dialog import VehicleDialog


def space_colour(space):
    """Status first (unavailable/occupied/reserved), then special type for free spaces."""
    if space["unavailable"]:
        return UNAVAIL
    if space["occupied"]:
        return OCCU
    if space["reserved"]:
        return RES
    if space["accessible"]:
        return ACCESS
    if space["ev"]:
        return EVCHA
    return AVAIL


def yes_no(flag):
    return "Yes" if flag else "No"


class ParkingLayoutPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG)
        self.app = app
        self.selected_id = None
        self.reserve_var = tk.StringVar()

        top = tk.Frame(self, bg=BG)
        top.pack(fill="x")
        tk.Label(top, text="Parking Layout", bg=BG, fg=TEXT, font=("Segoe UI", 20, "bold")).pack(side="left")
        tk.Button(top, text="+ Park Vehicle (AI)", command=lambda: VehicleDialog(app, self.after_assign),
                  bg=ACCENT, fg="black", relief="flat", padx=12, pady=6).pack(side="right")

        legend = tk.Frame(self, bg=BG)
        legend.pack(anchor="w", pady=8)
        for text, colour in [("Available", AVAIL), ("Occupied", OCCU), ("Reserved", RES),
                             ("EV charging", EVCHA), ("Accessible", ACCESS), ("Unavailable", UNAVAIL)]:
            tk.Label(legend, text="  ", bg=colour).pack(side="left")
            tk.Label(legend, text=text + "   ", bg=BG, fg=MUTED).pack(side="left")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        grid = tk.Frame(body, bg=BG)
        grid.pack(side="left", anchor="n")
        self.cards = {}
        for space in app.parking.spaces:
            card = tk.Label(grid, width=12, height=4, font=("Lexend", 10, "bold"), fg="white", cursor="hand2",
                            highlightthickness=3, highlightbackground=BG)
            card.grid(row=space["row"], column=space["col"], padx=5, pady=5)
            card.bind("<Button-1>", lambda event, sid=space["id"]: self.select(sid))
            self.cards[space["id"]] = card

        self.panel = tk.Frame(body, bg=PANEL, padx=15, pady=12, width=280)
        self.panel.pack(side="left", fill="both", expand=True, padx=(20, 0))
        self.panel.pack_propagate(False)

    def select(self, space_id):
        self.selected_id = space_id
        self.refresh()

    def after_assign(self, space_id):
        """Called by the dialog after a vehicle was assigned: refresh everything and select the space."""
        self.selected_id = space_id
        self.app.refresh_all()

    def do(self, action):
        """Run an action on the selected space, show any error, then refresh all pages."""
        try:
            action(self.selected_id)
        except ValueError as error:
            messagebox.showerror("Action failed", str(error))
            return
        self.app.refresh_all()

    def refresh(self):
        for space in self.app.parking.spaces:
            tags = ("EV " if space["ev"] else "") + ("♿" if space["accessible"] else "")
            if space["unavailable"]:
                status = "UNAVAILABLE"
            elif space["occupied"]:
                status = space["vehicle"]
            elif space["reserved"]:
                status = "Reserved"
            else:
                status = "Free"
            selected = space["id"] == self.selected_id
            self.cards[space["id"]].config(bg=space_colour(space), text=f"{space['id']}\n{space['size']} {tags}\n{status}",
                                           highlightbackground="white" if selected else BG)
        self.show_details()

    def show_details(self):
        """Rebuild the right-hand panel for the selected space."""
        for widget in self.panel.winfo_children():
            widget.destroy()
        if self.selected_id is None:
            tk.Label(self.panel, text="Click a space to see its details.", bg=PANEL, fg=MUTED).pack(anchor="w")
            return
        space = self.app.parking.get_space(self.selected_id)
        status = ("Unavailable" if space["unavailable"] else "Occupied" if space["occupied"]
                  else f"Reserved for {space['reserved_for']}" if space["reserved"] else "Available")
        tk.Label(self.panel, text=f"Space {space['id']}", bg=PANEL, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        info = (f"Status: {status}\nSize: {space['size']}\nEV charging: {yes_no(space['ev'])}\n"
                f"Accessible: {yes_no(space['accessible'])}")
        tk.Label(self.panel, text=info, bg=PANEL, fg=TEXT, justify="left").pack(anchor="w", pady=6)

        if space["occupied"]:
            vehicle = self.app.vehicles.get(space["vehicle"])
            tk.Label(self.panel, text="Vehicle", bg=PANEL, fg=ACCENT, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(8, 0))
            if vehicle:
                text = (f"Plate: {vehicle['plate']}\nType: {vehicle['type']}\nSize: {vehicle['size']}\n"
                        f"EV: {yes_no(vehicle['is_ev'])}\nCharging required: {yes_no(vehicle['needs_charging'])}\n"
                        f"Accessibility required: {yes_no(vehicle['needs_access'])}\nPriority: {vehicle['priority']}")
            else:
                text = f"Plate: {space['vehicle']}\n(no registered details)"
            tk.Label(self.panel, text=text, bg=PANEL, fg=TEXT, justify="left").pack(anchor="w", pady=6)
            self.make_button("Release Space", lambda: self.do(self.app.allocator.release), OCCU, "black")
        elif space["unavailable"]:
            self.make_button("Make Available", lambda: self.do(lambda sid: self.app.parking.set_unavailable(sid, False)), ACCENT, "black")
        elif space["reserved"]:
            self.make_button("Cancel Reservation", lambda: self.do(self.app.parking.cancel_reservation), RES, "black")
        else:
            tk.Label(self.panel, text="Reserve for registration no.:", bg=PANEL, fg=MUTED).pack(anchor="w", pady=(10, 2))
            self.reserve_var.set("")
            ttk.Entry(self.panel, textvariable=self.reserve_var).pack(fill="x")
            self.make_button("Reserve", lambda: self.do(lambda sid: self.app.parking.reserve(
                sid, self.reserve_var.get().strip().upper())), RES, "black")
            self.make_button("Mark Unavailable", lambda: self.do(lambda sid: self.app.parking.set_unavailable(sid, True)), UNAVAIL, "black")

    def make_button(self, text, command, colour, text_colour):
        tk.Button(self.panel, text=text, command=command, bg=colour, fg=text_colour, relief="flat",
                  pady=6).pack(fill="x", pady=4)
