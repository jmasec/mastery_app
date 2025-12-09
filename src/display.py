import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from ..lib.user import User, make_new_user, make_user_from_db, add_container_db
from ..lib.mastery_container import MasteryContainer
from ..lib.mastery_db import MasteryDB


class App:
    def __init__(self, root, db, user = None):
        if user is None:
            user = make_new_user("Default", db)

        self.root = root
        self.root.title("Mastery Tracker")

        self.progress_values = {} 
        self.timer_running = False
        self.timer_start_time = None
        self.user = user
        self.db = db
        self.max_hours = 10000.0

        for key,val in user.containers.items():
            self.progress_values[key] = val.xp_level

        # Build UI
        self.create_user_section()
        self.create_update_section()
        self.create_timer_section()
        self.create_add_bar_section()
        self.create_delete_bar_section()
        self.create_progress_section()

        self.refresh_ui()

    # ===============================================================
    # Dynamic Progress Bars
    # ===============================================================

    def create_progress_section(self):
        # Frame for all progress bars
        self.progress_frame = ttk.LabelFrame(self.root, text="Progress Bars")
        self.progress_frame.pack(fill="x", padx=10, pady=10)

        # Store widgets for each bar
        self.bar_widgets = {}

        # Clear dropdown menus so we can repopulate them
        manual_menu = self.update_bar_dropdown["menu"]
        manual_menu.delete(0, "end")

        timer_menu = self.timer_target_dropdown["menu"]
        timer_menu.delete(0, "end")

        for key, val in self.progress_values.items():

            # Row frame for each progress bar
            row = ttk.Frame(self.progress_frame)
            row.pack(fill="x", pady=5)

            # Label with bar name
            name_label = ttk.Label(row, text=key, width=15)
            name_label.pack(side="left")

            # Progress bar widget
            bar = ttk.Progressbar(row, maximum=10000.0)
            bar.pack(side="left", fill="x", expand=True)

            # Clamp value 0–100 (or higher if you use hour/min conversion)
            normalized = max(0.0, min(100.0, float(val)))
            bar["value"] = normalized * 100  # multiplied by 100 for precision

            level_text = self.user.containers[key].level if key in self.user.containers else "Novice"
            level_label = ttk.Label(row, text=level_text, width=12)
            level_label.pack(side="left", padx=5)

            # Value label showing hours/minutes/float
            value_label = ttk.Label(row, text=f"{val:.2f}")
            value_label.pack(side="right", padx=5)

            # Save widgets for later updates
            self.bar_widgets[key] = {
                "frame": row,
                "label": name_label,
                "bar": bar,
                "value_label": value_label,
                "level_label": level_label,
            }

            # Add to manual dropdown
            manual_menu.add_command(
                label=key, command=lambda v=key: self.selected_bar.set(v)
            )

            # Add to timer dropdown
            timer_menu.add_command(
                label=key, command=lambda v=key: self.timer_target.set(v)
            )

            # Default timer target if none selected
            if not self.timer_target.get():
                self.timer_target.set(key)
            
        # === Delete bar dropdown ===
        delete_menu = self.delete_bar_dropdown["menu"]
        delete_menu.delete(0, "end")

        for key in self.progress_values.keys():
            delete_menu.add_command(
                label=key,
                command=lambda v=key: self.delete_bar_var.set(v)
            )

        # Set default if none
        if not self.delete_bar_var.get() and self.progress_values:
            first = list(self.progress_values.keys())[0]
            self.delete_bar_var.set(first)



    def add_progress_bar(self, name):
        if name in self.progress_values:
            print("Bar already exists.")
            return

        # Initialize value
        self.progress_values[name] = 0.0

        # === Match layout of create_progress_section ===
        row = ttk.Frame(self.progress_frame)
        row.pack(fill="x", pady=5)

        # Name label (left)
        name_label = ttk.Label(row, text=name, width=15)
        name_label.pack(side="left")

        # Progress bar (middle)
        bar = ttk.Progressbar(row, maximum=10000.0)
        bar.pack(side="left", fill="x", expand=True)

        level_lbl = ttk.Label(row, text="Novice", width=12)
        level_lbl.pack(side="left", padx=5)

        # Value label (right)
        value_label = ttk.Label(row, text="0h 0m")
        value_label.pack(side="right", padx=5)

        # Store widgets
        self.bar_widgets[name] = {
            "frame": row,
            "label": name_label,
            "bar": bar,
            "value_label": value_label,
            "level_label": level_lbl,
        }

        # Add to dropdowns
        manual_menu = self.update_bar_dropdown["menu"]
        manual_menu.add_command(
            label=name, command=lambda v=name: self.selected_bar.set(v)
        )

        timer_menu = self.timer_target_dropdown["menu"]
        timer_menu.add_command(
            label=name, command=lambda v=name: self.timer_target.set(v)
        )

        # Default timer target if none set
        if not self.timer_target.get():
            self.timer_target.set(name)

        # Add to user model
        container : MasteryContainer | None = self.user.new_container(name)
        if container:
            add_container_db(container.uuid, self.user, name, self.db)

        # Refresh UI
        self.refresh_ui()


    def format_hours_minutes(self, value_float):
        """
        Converts a float into:
        - decimal hours
        - hours + minutes (rounded)

        Example:
            1.75 → "1.75h (1h 45m)"
        """
        hours = int(value_float)
        minutes = int((value_float - hours) * 60)

        return f"{value_float:.2f}h ({hours}h {minutes}m)"


    # ===============================================================
    # Add Bar UI
    # ===============================================================
    def create_add_bar_section(self):
        frame = ttk.LabelFrame(self.root, text="Add New XP Bar")
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="XP Bar Name:").pack(side="left", padx=5)

        self.new_bar_entry = ttk.Entry(frame, width=20)
        self.new_bar_entry.pack(side="left", padx=5)

        ttk.Button(frame, text="Add", command=self.add_new_bar_clicked).pack(side="left")

    def add_new_bar_clicked(self):
        name = self.new_bar_entry.get().strip()
        if name:
            self.add_progress_bar(name)
            self.new_bar_entry.delete(0, tk.END)

    # ===============================================================
    # Delete Bar UI
    # ===============================================================
    def create_delete_bar_section(self):
        frame = ttk.LabelFrame(self.root, text="Delete XP Bar")
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="Select bar:").pack(side="left", padx=5)

        self.delete_bar_var = tk.StringVar(value="")

        self.delete_bar_dropdown = tk.OptionMenu(frame, self.delete_bar_var, "")
        self.delete_bar_dropdown.pack(side="left", padx=5)

        ttk.Button(frame, text="Delete", command=self.delete_selected_bar).pack(side="left")


    def delete_selected_bar(self):
        name = self.delete_bar_var.get()
        if not name:
            messagebox.showerror("Error", "No bar selected.")
            return

        if name not in self.progress_values:
            messagebox.showerror("Error", "Bar not found.")
            return

        uuid_to_delete = self.user.containers[name].uuid

        # Remove UI
        widgets = self.bar_widgets.pop(name)
        widgets["frame"].destroy()

        # Remove backend data
        self.progress_values.pop(name, None)
        self.user.containers.pop(name, None)

        # Remove from database
        self.db.delete_container_db(str(uuid_to_delete))

        self.rebuild_all_dropdowns()
        
        self.refresh_ui()



    def rebuild_all_dropdowns(self):
        # --- Manual update dropdown ---
        manual_menu = self.update_bar_dropdown["menu"]
        manual_menu.delete(0, "end")

        # --- Timer dropdown ---
        timer_menu = self.timer_target_dropdown["menu"]
        timer_menu.delete(0, "end")

        # --- Delete dropdown ---
        delete_menu = self.delete_bar_dropdown["menu"]
        delete_menu.delete(0, "end")

        # Re-add all current bars
        for name in self.progress_values.keys():
            manual_menu.add_command(
                label=name,
                command=lambda v=name: self.selected_bar.set(v)
            )
            timer_menu.add_command(
                label=name,
                command=lambda v=name: self.timer_target.set(v)
            )
            delete_menu.add_command(
                label=name,
                command=lambda v=name: self.delete_bar_var.set(v)
            )

        # If nothing selected, reset
        if self.selected_bar.get() not in self.progress_values:
            self.selected_bar.set("")

        if self.timer_target.get() not in self.progress_values:
            self.timer_target.set("")

        if self.delete_bar_var.get() not in self.progress_values:
            self.delete_bar_var.set("")



    # ===============================================================
    # Manual Update UI
    # ===============================================================
    def create_update_section(self):
        frame = ttk.LabelFrame(self.root, text="Add XP (hh:mm)")
        frame.pack(fill="x", padx=10, pady=10)

        self.selected_bar = tk.StringVar(value="")

        self.update_bar_dropdown = tk.OptionMenu(frame, self.selected_bar, "")
        self.update_bar_dropdown.pack(side="left", padx=5)

        self.value_entry = ttk.Entry(frame, width=10)
        self.value_entry.pack(side="left", padx=5)

        ttk.Button(frame, text="Update", command=self.manual_update).pack(side="left")

    def manual_update(self):
        bar_name = self.selected_bar.get()
        if not bar_name:
            print("No bar selected")
            return

        try:
            # Convert "4000.45" → 4000h + 45m → float hours
            hours_to_add = self.parse_hours_minutes(self.value_entry.get())
        except ValueError:
            print("Invalid number format")
            return

        # Clamp to 0–10,000 hours increment
        hours_to_add = max(0.0, min(10000.0, hours_to_add))

        # Apply increment to progress bar
        self.progress_values[bar_name] += hours_to_add
        self.progress_values[bar_name] = min(10000.0, self.progress_values[bar_name])

        # Apply to your user object
        self.user.containers[bar_name].update_xp_level(hours_to_add)
        self.db.update_container_db(str(self.user.containers[bar_name].uuid), self.user.containers[bar_name].xp_level ,self.user.containers[bar_name].level)

        # Refresh UI
        self.refresh_ui()


    def create_user_section(self):
        frame = ttk.LabelFrame(self.root, text="User")
        frame.pack(fill="x", padx=10, pady=10)

        self.username_label = ttk.Label(frame, text="")
        self.username_label.pack(side="left", padx=5)

        ttk.Button(
            frame, 
            text="Change Username", 
            command=self.open_username_popup
        ).pack(side="right", padx=10)

    def open_username_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Change Username")
        popup.geometry("300x150")
        popup.grab_set()   # make the window modal

        ttk.Label(popup, text="Enter new username:").pack(pady=10)

        entry = ttk.Entry(popup, width=25)
        entry.pack()
        entry.focus()

        def save_and_close():
            new_name = entry.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Username cannot be empty.")
                return

            # Update user object
            self.user.update_username(new_name)
            self.db.update_user_db(self.user.uuid, new_name)

            # Refresh UI label
            self.username_label.config(text=new_name)

            popup.destroy()

        ttk.Button(popup, text="Save", command=save_and_close).pack(pady=10)

        popup.bind("<Return>", lambda e: save_and_close())

    # ===============================================================
    # Timer UI + Timer Linking to Bar
    # ===============================================================
    def create_timer_section(self):
        frame = ttk.LabelFrame(self.root, text="Timer")
        frame.pack(fill="x", padx=10, pady=10)

        self.timer_label = ttk.Label(frame, text="00:00")
        self.timer_label.pack(side="left", padx=10)

        ttk.Button(frame, text="Start", command=self.start_timer).pack(side="left")
        ttk.Button(frame, text="Stop", command=self.stop_timer).pack(side="left")

        ttk.Label(frame, text="XP bar:").pack(side="left", padx=10)

        # Dropdown of which bar the timer updates
        self.timer_target = tk.StringVar(value="")
        self.timer_target_dropdown = tk.OptionMenu(frame, self.timer_target, "")
        self.timer_target_dropdown.pack(side="left")

    def start_timer(self):
        if self.timer_running:
            return

        if not self.timer_target.get():
            print("No bar selected for timer!")
            return

        self.timer_running = True
        self.timer_start_time = time.time()

        threading.Thread(target=self.timer_loop, daemon=True).start()

    def timer_loop(self):
        last_update = time.time()

        while self.timer_running:
            now = time.time()

            # Seconds passed since last iteration
            delta = now - last_update
            last_update = now

            # Timer display HH:MM:SS
            total_elapsed = int(now - self.timer_start_time)

            hrs = total_elapsed // 3600
            mins = (total_elapsed % 3600) // 60
            secs = total_elapsed % 60

            self.timer_label.config(text=f"{hrs:02d}:{mins:02d}:{secs:02d}")

            target = self.timer_target.get()
            if target:

                # Convert *this chunk of time* to hours
                hours_increment = delta / 3600.0

                # Add it to the bar's stored hours
                self.progress_values[target] += hours_increment

                # Ensure in 0–10,000 range
                self.progress_values[target] = min(10000.0, max(0.0, self.progress_values[target]))

                # Update bar + label
                self.refresh_ui()

            time.sleep(0.2)



    def stop_timer(self):
        if not self.timer_running:
            return

        self.timer_running = False

        elapsed = int(time.time() - self.timer_start_time) # type: ignore

        # finalize bar value
        target = self.timer_target.get()
        # if target:
        #     self.progress_values[target] += min(100, elapsed)

        self.refresh_ui()

    # ===============================================================
    # Refresh UI
    # ===============================================================
    def refresh_ui(self):
        for name, widgets in self.bar_widgets.items():
            hours = self.progress_values.get(name, 0.0)

            # Set bar value directly in hours (progressbar max = 10000)
            widgets["bar"]["value"] = hours

            # Display pretty formatted HHh MMm
            widgets["value_label"].config(
                text=self.format_hours_minutes(hours)
            )

            widgets["level_label"].config(
                text=self.user.containers[name].level
            )

        # Show username if you have a User object
        if self.user:
            self.username_label.config(text=self.user.username)

            # ------ Delete Dropdown ------
        delete_menu = self.delete_bar_dropdown["menu"]
        delete_menu.delete(0, "end")

        for key in self.progress_values.keys():
            delete_menu.add_command(
                label=key,
                command=lambda v=key: self.delete_bar_var.set(v)
            )

        if self.progress_values and not self.delete_bar_var.get():
            self.delete_bar_var.set(next(iter(self.progress_values)))


    def parse_hours_minutes(self, text):
        """
        Parse user input like '4000.45' meaning 4000 hours + 45 minutes.
        Returns float hours.
        """
        try:
            if "." not in text:
                # Whole number → pure hours
                return float(text)

            hours_str, mins_str = text.split(".", 1)

            hours = int(hours_str)
            minutes = int(mins_str)

            # Clamp minutes 0–59 (normalize overflow)
            if minutes >= 60:
                hours += minutes // 60
                minutes = minutes % 60

            return hours + (minutes / 60.0)

        except Exception:
            raise ValueError("Invalid hours.minutes format")


# ===============================================================
# Run
# ===============================================================
