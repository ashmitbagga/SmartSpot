import tkinter as tk
from gui.theme import BG, PANEL, TEXT, ACCENT, setup_style
from gui.dashboard import DashboardPage
from gui.parking_layout import ParkingLayoutPage
from modules.parking_manager import ParkingManager
from modules.vehicle_manager import VehicleManager
from modules.allocation_manager import AllocationManager


class SmartSpotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SmartSpot - Smart Parking Allocation System")
        self.geometry("1100x720")
        setup_style(self)
        # data is loaded from JSON
        self.parking = ParkingManager()
        self.vehicles = VehicleManager()
        self.allocator = AllocationManager(self.parking, self.vehicles)

        sidebar = tk.Frame(self, bg=PANEL, width=190)
        sidebar.pack(side="left", fill="y")
        tk.Label(sidebar, text="SmartSpot", bg=PANEL, fg=ACCENT, font=("Segoe UI", 18, "bold")).pack(pady=20)
        content = tk.Frame(self, bg=BG, padx=25, pady=20)
        content.pack(side="left", fill="both", expand=True)
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)

        self.pages = {}
        page_classes = [("Dashboard", DashboardPage), ("Parking Layout", ParkingLayoutPage)]
        for name, page_class in page_classes:
            page = page_class(content, self)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = page
            tk.Button(sidebar, text=name, command=lambda n=name: self.show_page(n), bg=PANEL, fg=TEXT,
                       relief="flat", anchor="w",
                      padx=20, pady=10).pack(fill="x")
        self.refresh_all()
        self.show_page("Dashboard")

    def show_page(self, name):
        self.pages[name].tkraise()

    def refresh_all(self):
        for page in self.pages.values():
            page.refresh()


if __name__ == "__main__":
    SmartSpotApp().mainloop()
