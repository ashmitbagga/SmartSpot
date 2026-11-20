"""Pop-up: register a vehicle, run CSP + Hill Climbing, and assign the chosen space."""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from algorithms.csp import HARD_CONSTRAINTS
from algorithms.relaxation import PENALTY
from gui.theme import BG, PANEL, TEXT, ACCENT, AVAIL, RES, OCCU


class VehicleDialog(tk.Toplevel):
    def __init__(self, app, on_assigned):
        super().__init__(app)
        self.app, self.on_assigned = app, on_assigned
        self.title("Park Vehicle - AI Allocation")
        self.configure(bg=BG, padx=15, pady=12)
        self.geometry("680x720")
        self.result = None

        form = tk.Frame(self, bg=BG)
        form.pack(anchor="w")
        self.plate = tk.StringVar()
        tk.Label(form, text="Registration number", bg=BG, fg=TEXT).grid(row=0, column=0, sticky="w", pady=3)
        entry = ttk.Entry(form, textvariable=self.plate, width=24)
        entry.grid(row=0, column=1, padx=10)
        entry.bind("<KeyRelease>", lambda e: self.reset_result())
        fields = {"Type": ("Car", ["Car", "SUV", "Bike"]), "Size": ("Medium", ["Small", "Medium", "Large"]),
                  "Is EV?": ("No", ["Yes", "No"]), "Charging required?": ("No", ["Yes", "No"]),
                  "Accessibility required?": ("No", ["Yes", "No"]), "Priority": ("Normal", ["Normal", "High"])}
        self.vars = {}
        for i, (label, (default, options)) in enumerate(fields.items(), start=1):
            tk.Label(form, text=label, bg=BG, fg=TEXT).grid(row=i, column=0, sticky="w", pady=3)
            var = tk.StringVar(value=default)
            ttk.Combobox(form, textvariable=var, values=options, state="readonly", width=21).grid(row=i, column=1, padx=10)
            self.vars[label] = var

        bar = tk.Frame(self, bg=BG)
        bar.pack(anchor="w", pady=8)
        tk.Button(bar, text="1. Register Vehicle", command=self.register, bg=PANEL, fg=TEXT, relief="flat", padx=10, pady=5).pack(side="left", padx=3)
        tk.Button(bar, text="2. Run AI Allocation", command=self.run_ai, bg=ACCENT, fg="black", relief="flat", padx=10, pady=5).pack(side="left", padx=3)
        self.assign_button = tk.Button(bar, text="3. Assign Space", command=self.assign, bg=AVAIL, fg="black", relief="flat",
                                       padx=10, pady=5, state="disabled")
        self.assign_button.pack(side="left", padx=3)

        self.output = ScrolledText(self, bg=PANEL, fg=TEXT, font=("Consolas", 10), wrap="word", relief="flat")
        self.output.pack(fill="both", expand=True)
        for tag, colour in [("head", ACCENT), ("good", AVAIL), ("bad", OCCU), ("warn", RES)]:
            self.output.tag_config(tag, foreground=colour)

    def write(self, text, tag=None):
        self.output.insert("end", text + "\n", tag)

    def reset_result(self):
        self.result = None
        self.assign_button.config(state="disabled")

    def register(self):
        v = self.vars
        try:
            vehicle = self.app.vehicles.register(self.plate.get(), v["Type"].get(), v["Size"].get(),
                                                 v["Is EV?"].get() == "Yes", v["Charging required?"].get() == "Yes",
                                                 v["Accessibility required?"].get() == "Yes", v["Priority"].get())
        except ValueError as error:
            messagebox.showerror("Cannot register", str(error), parent=self)
            return
        self.plate.set(vehicle["plate"])
        self.output.delete("1.0", "end")
        self.write(f"Vehicle {vehicle['plate']} registered. Now run the AI allocation.", "good")

    def run_ai(self):
        plate = self.plate.get().strip().upper()
        vehicle = self.app.vehicles.get(plate)
        if vehicle is None:
            messagebox.showwarning("Not registered", "Register the vehicle first.", parent=self)
            return
        if vehicle["space"]:
            messagebox.showwarning("Already parked", f"{plate} is already in {vehicle['space']}.", parent=self)
            return
        r = self.app.allocator.find_space(vehicle)   # uses the CURRENT parking state
        self.result, self.plate_used = r, plate
        self.assign_button.config(state="disabled")
        self.output.delete("1.0", "end")

        # STEP 1: CSP
        if r["csp_failed"]:
            self.write("STEP 1: CSP FAILED - no space satisfies ALL hard constraints", "bad")
        else:
            self.write("STEP 1: CSP - hard constraints", "head")
        for rule in HARD_CONSTRAINTS:
            self.write("  - " + rule)
        self.write(f"Checked: {r['checked']}   Valid: {len(r['valid'])}   Rejected: {len(r['rejected'])}")
        self.write("Valid: " + (", ".join(r["valid"]) or "none"), "good" if r["valid"] else "bad")
        self.write("Rejected:", "bad")
        for space_id, reasons in r["rejected"]:
            self.write(f"  {space_id}: " + "; ".join(reasons))

        # STEP 2 (only when CSP failed): explain why, then relax and continue
        step = 2
        if r["csp_failed"]:
            self.write("\nWhy CSP failed (each requirement checked on its own):", "warn")
            for label, count in r["diagnosis"]:
                self.write(f"  {label}: {count}")
            self.write("  ...but no space meets all of them together.")
            if r["best"] is None:
                self.write("\nFALLBACK also failed: even after relaxing charging/accessibility there is no free, "
                           "unreserved space that fits this vehicle's size.", "bad")
                return
            self.write("\nSTEP 2: FALLBACK - relax constraints", "head")
            self.write(f"Charging and accessibility become penalised preferences (-{PENALTY} points each).")
            self.write("Size, availability and reservations are never relaxed.")
            self.write("Candidates: " + ", ".join(r["candidates"]))
            step = 3
        elif r["best"] is None:
            return

        self.write(f"\nSTEP {step}: Hill Climbing steps", "head")
        for line in r["log"]:
            self.write(line)
        self.write("\nFINAL RESULT", "head")
        self.write(f"Assigned space: {r['best']}   Score: {r['score']} / 100", "good")
        if r["csp_failed"]:
            self.write("COMPROMISE - these requirements are NOT met: " + "; ".join(r["relaxed"]), "warn")
        self.write("Constraints satisfied:")
        for line in r["satisfied"]:
            self.write("  + " + line)
        self.write("Why selected:")
        for line in r["explanation"]:
            self.write("  * " + line)
        self.write("Other candidate spaces:", "warn")
        for space_id, score, note in r["others"]:
            self.write(f"  {space_id}: {score}" + (f"  (not met: {note})" if note else ""))
        self.assign_button.config(state="normal")

    def assign(self):
        if not self.result or not self.result["best"]:
            return
        if self.result["csp_failed"]:
            question = ("This is a compromise. Not met: " + "; ".join(self.result["relaxed"]) +
                        f"\n\nAssign {self.result['best']} anyway?")
            if not messagebox.askyesno("Assign compromise space?", question, parent=self):
                return
        try:
            self.app.allocator.assign(self.plate_used, self.result["best"])
        except ValueError as error:
            messagebox.showerror("Cannot assign", str(error), parent=self)
            return
        self.on_assigned(self.result["best"])
        self.destroy()
