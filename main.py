# If you're reading this, you stink.
# Created by @iDatMelon and @Claude

import ctypes
import os
import random
import struct
import sys
import tkinter as tk
from ctypes import wintypes

import customtkinter as ctk
from PIL import Image, ImageTk

VERSION = "v9.1.0"

CONFIG = {
    "title": "USAR Ribbon Rack Builder",
    "size": "1180x760",
    "minimum_size": (960, 640),
    "ribbon_size": (13, 3),
    "ribbons_per_row": 3,
    "preview_scale": 6,
}

RIBBON_TABLE = [
    ("Medal of Honor", "moh.png", None , None),
    ("Army Distinguished Service Cross", "adsc.png", ("Leaves", 9), None),
    ("Defense Distinguished Service", "dds.png", ("Leaves", 9), None),
    ("Army Distinguished Service", "ads.png", ("Leaves", 9), None),
    ("Silver Star", "silverstar.png", ("Leaves", 9), None),
    ("Defense Superior Service", "defensesuperiorservice.png", ("Leaves", 9), None),
    ("Legion of Merit", "lom.png", ("Leaves", 9), None),
    ("Distinguished Flying Cross", "distinguishedflyingcross.png", ("Leaves", 9), None),
    ("Soldier Medal", "soldiermedal.png", ("Leaves", 9), None),
    ("Bronze Star", "bronzestar.png", ("Leaves", 9), None),
    ("Purple Heart", "purpleheart.png", None, None),
    ("Defense Meritorious Service", "dms.png", ("Leaves", 9), None),
    ("Meritorious Service", "ms.png", ("Leaves", 9), None),
    ("Air Medal", "airmedal.png", ("Leaves", 9), None),
    ("Joint Service Commendation", "jointservicecommendation.png", ("Leaves", 9), None),
    ("Army Commendation", "commendation.png", ("Leaves", 9), None),
    ("Joint Service Achievement", "jsa.png", ("Leaves", 9), None),
    ("Army Achievement", "achievement.png", ("Leaves", 9), None),
    ("Public Service Commendation Medal", "publicservice.png", ("Leaves", 9), None),
    ("War Games", "wargames.png", ("Leaves", 9), None),
    ("Army Good Conduct", "goodconduct.png", ("AGC", 6), None),
    ("Army Occupation Ribbon", "occupation.png", ("Leaves", 9), None),
    ("Military Justice Ribbon", "mjr.png", None, None),
    ("National Defense Service", "nds.png", None, None),
    ("Antarctica Service", "antartica.png", ("OtherStars", 4), None),
    ("Armed Forces Expeditionary Medal", "armedforcesexpeditionary.png", None, None),
    ("South West Asia Service", "swasia.png", ("Deployment", 3), None),
    ("Kosovo Campaign", "kosovo.png", ("Deployment", 3), None),
    ("Afghanistan Campaign", "afghanistan.png", ("Deployment", 3), None),
    ("Iraq Campaign", "iraq.png", ("Deployment", 3), None),
    ("Joint Special Operations Campaign", "jsoc.png", ("Deployment", 3), None),
    ("GWT Expeditionary", "gwtexpeditionary.png", None, None),
    ("GWT Service", "gwtservice.png", None, None),
    ("Armed Forces Service Ribbon", "forcesservice.png", ("OtherStars", 4), None),
    ("Humanitarian Service Ribbon", "humanitarian.png", ("OtherStars", 4), None),
    ("Outstanding Volunteer", "outstandingvolunteer.png", ("Leaves", 9), None),
    ("Army Recruiting Ribbon", "recruiting.png", None, None),
    ("Army Sea Duty", "seaduty.png", ("Deployment", 3), None),
    ("NCO Professional Development", "NCOribbon.png", None, None),
    ("Army Service", "armyservice.png", None, None),
    ("Oversea Service", "overseas.png", None, None),
    ("Combat Readiness", "combatreadiness.png", None, None),
    ("Order of the British Empire", "britishempire.png", None, None),
    ("Queens Dedication Medal", "queensdedication.png", None, None),
    ("Turkish Marksmanship", "turkish.png", ("TM", 4), None),
    ("UN Ribbon", "UN.png", None, None),
    ("NATO MS", "NATOms.png", None, None),
    ("NATO Non Article 5", "non_ar-5.png", (os.path.join("NATO", "NonAR-5"), 3), None),
    ("NATO Article 5", "ar-5.png", (os.path.join("NATO", "AR-5"), 3), None),
    ("Kuwait Liberation Ribbon", "kuwait.png", None, None),
    ("Legion of Merit Officer", "lom_officer.png", None, "Legion of Merit"),
    ("Legion of Merit Commander", "lom_commander.png", None, "Legion of Merit"),
]

RIBBON_NAMES = [name for name, _, _, variant_of in RIBBON_TABLE if variant_of is None]
ORDER_OF_PRECEDENCE = {name: i + 1 for i, name in enumerate(RIBBON_NAMES)}
RIBBON_FILES = {name: filename for name, filename, _, _ in RIBBON_TABLE}
DEVICE_CONFIG = {
    name: device for name, _, device, variant_of in RIBBON_TABLE
    if device is not None and variant_of is None
}

PRESETS = {
    "E2+ Ribbons": ["National Defense Service", "GWT Service", "Army Service"],
    "Deployment Ribbons": ["GWT Expeditionary", "Oversea Service", "Armed Forces Expeditionary Medal"],
    "NCO Ribbon": ["NCO Professional Development"],
}

def resource_path(relative_path):
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return os.path.join(base, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


if getattr(sys, "frozen", False):
    try:
        os.chdir(os.path.dirname(sys.executable))
    except OSError:
        pass


def load_rgba(path, size=None):
    with Image.open(path) as source:
        image = source.convert("RGBA")
    if size:
        image = image.resize(size, Image.Resampling.NEAREST)
    return image


def safe_filename(value, fallback):
    cleaned = "".join(char for char in value.strip() if char.isalnum() or char in "_-").lower()
    return cleaned or fallback


class RibbonRackBuilder:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.withdraw()
        self.root.title(CONFIG["title"])
        self.root.geometry(CONFIG["size"])
        self.root.minsize(*CONFIG["minimum_size"])

        self._set_icon()

        self.ribbon_vars = {name: ctk.BooleanVar(value=False) for name in RIBBON_NAMES}
        self.device_vars = {name: ctk.StringVar(value="x1") for name in DEVICE_CONFIG}
        self.lom_variant = ctk.StringVar(value="Legion of Merit")
        self.offset_var = ctk.BooleanVar(value=False)
        self.output_name = ctk.StringVar(value="")
        self.preset_vars = {name: ctk.BooleanVar(value=False) for name in PRESETS}
        self.base_ribbon_cache = {}
        self.scaled_ribbon_cache = {}
        self.device_cache = {}
        self.preview_photos = []
        self.status_after_id = None

        self._build_ui()
        self.redraw_preview()
        self._show_startup_animation()

    def _show_startup_animation(self):
        splash = ctk.CTkToplevel(self.root)
        splash.overrideredirect(True)
        splash.configure(fg_color="#17191E")
        splash.geometry("440x270")
        splash.update_idletasks()
        x = (splash.winfo_screenwidth() - 440) // 2
        y = (splash.winfo_screenheight() - 270) // 2
        splash.geometry(f"440x270+{x}+{y}")

        ctk.CTkLabel(
            splash, text="QMC", text_color="#78A9FF",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(28, 4))
        ctk.CTkLabel(
            splash, text=f"Ribbon Rack Builder | {VERSION}",
            font=ctk.CTkFont(size=23, weight="bold")
        ).pack()

        ribbon_size = self._image_size(scaled=True)
        column_gap = 6
        row_gap = 8
        canvas_width = ribbon_size[0] * 3 + column_gap * 2
        canvas_height = ribbon_size[1] * 3 + row_gap * 2
        rack_canvas = tk.Canvas(
            splash, width=canvas_width, height=canvas_height,
            bg="#17191E", highlightthickness=0
        )
        rack_canvas.pack(pady=(18, 8))
        ribbon_photos = []
        ribbon_items = []
        for index, name in enumerate(random.sample(RIBBON_NAMES, 9)):
            row, column = divmod(index, 3)
            photo = ImageTk.PhotoImage(self._ribbon_image(name, scaled=True))
            ribbon_photos.append(photo)
            x = column * (ribbon_size[0] + column_gap)
            y = row * (ribbon_size[1] + row_gap)
            ribbon_items.append(rack_canvas.create_image(
                x, y, image=photo, anchor="nw", state="hidden"
            ))
        self._splash_ribbon_photos = ribbon_photos
        random.shuffle(ribbon_items)

        ctk.CTkLabel(
            splash, text="Loading...", text_color=("gray45", "gray70"),
            font=ctk.CTkFont(size=12)
        ).pack(pady=(4, 0))

        def reveal_ribbon(index=0):
            if not splash.winfo_exists():
                return
            if index == len(ribbon_items):
                splash.after(1230, finish)
                return
            rack_canvas.itemconfigure(ribbon_items[index], state="normal")
            splash.after(75, lambda: reveal_ribbon(index + 1))

        def finish():
            if splash.winfo_exists():
                splash.destroy()
            self._splash_ribbon_photos.clear()
            self.root.deiconify()
            self.root.lift()

        splash.after(100, reveal_ribbon)

    def _set_icon(self):
        path = resource_path("icon.ico")
        if not os.path.exists(path):
            return
        try:
            self.root.iconbitmap(path)
        except tk.TclError:
            try:
                self._icon_image = ImageTk.PhotoImage(load_rgba(path))
                self.root.iconphoto(False, self._icon_image)
            except Exception:
                pass

    def _build_ui(self):
        self.root.grid_columnconfigure(0, weight=6)
        self.root.grid_columnconfigure(1, weight=5)
        self.root.grid_rowconfigure(0, weight=1)

        self.ribbons_panel = ctk.CTkFrame(self.root, corner_radius=12)
        self.ribbons_panel.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)
        self.ribbons_panel.grid_rowconfigure(1, weight=1)
        self.ribbons_panel.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkFrame(self.ribbons_panel, fg_color="transparent")
        heading.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 8))
        ctk.CTkLabel(
            heading, text="USAR Ribbon Rack Builder", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            heading, text=f"Managed and maintained by @iDatMelon | Version {VERSION}",
            text_color=("gray40", "gray70"), font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(2, 10))

        actions = ctk.CTkFrame(heading, fg_color="transparent")
        actions.pack(anchor="w")
        ctk.CTkButton(actions, text="Select all", width=92, height=30, command=self.select_all).pack(
            side="left", padx=(0, 6)
        )
        ctk.CTkButton(
            actions, text="Clear", width=74, height=30, fg_color="gray30",
            hover_color="gray25", command=self.deselect_all
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            actions, text="Reset devices", width=110, height=30, fg_color="gray30",
            hover_color="gray25", command=self.reset_devices
        ).pack(side="left", padx=6)

        self.ribbon_scroll = ctk.CTkScrollableFrame(
            self.ribbons_panel, label_text="RIBBONS", corner_radius=8
        )
        self.ribbon_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        for name in sorted(RIBBON_NAMES, key=self.precedence_key):
            self._add_ribbon_row(name)

        self.output_panel = ctk.CTkFrame(self.root, corner_radius=12)
        self.output_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)
        self.output_panel.grid_columnconfigure(0, weight=1)
        self.output_panel.grid_rowconfigure(1, weight=1)

        preview_heading = ctk.CTkFrame(self.output_panel, fg_color="transparent")
        preview_heading.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 8))
        preview_heading.grid_columnconfigure(0, weight=1)
        preview_details = ctk.CTkFrame(preview_heading, fg_color="transparent")
        preview_details.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            preview_details, text="Preview:", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w")
        self.selection_label = ctk.CTkLabel(
            preview_details, text="0 ribbons selected", text_color=("gray40", "gray70"),
            font=ctk.CTkFont(size=12)
        )
        self.selection_label.pack(anchor="w", pady=(2, 0))

        offset_control = ctk.CTkFrame(
            preview_heading, corner_radius=8, fg_color=("gray90", "#17191E")
        )
        offset_control.grid(row=0, column=1, sticky="e", padx=(12, 0), pady=2)
        ctk.CTkCheckBox(
            offset_control, text="NEW! Offset Ribbons", variable=self.offset_var,
            command=self.redraw_preview, font=ctk.CTkFont(size=13, weight="bold"),
            checkbox_width=18, checkbox_height=18
        ).pack(padx=10, pady=7)

        self.preview_canvas = tk.Canvas(
            self.output_panel, bg="#17191E", highlightthickness=0, bd=0
        )
        self.preview_canvas.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 12))
        self.preview_canvas.bind("<Configure>", lambda _event: self.redraw_preview())

        footer = ctk.CTkFrame(self.output_panel, corner_radius=10)
        footer.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))
        footer.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            footer, text="Presets:", font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        for index, (preset_name, ribbon_list) in enumerate(PRESETS.items(), start=1):
            ctk.CTkCheckBox(
                footer, text=preset_name, variable=self.preset_vars[preset_name],
                command=lambda n=preset_name: self.toggle_preset(n)
            ).grid(row=index, column=0, sticky="w", padx=12, pady=3)
        save_controls = ctk.CTkFrame(footer, fg_color="transparent")
        save_controls.grid(row=1, column=1, rowspan=4, sticky="ne", padx=12, pady=(10, 8))
        ctk.CTkLabel(
            save_controls, text="EXPORT",
            font=ctk.CTkFont(size=11, weight="bold"), text_color=("gray45", "gray65")
        ).pack(anchor="w", pady=(0, 6))
        filename_field = ctk.CTkFrame(save_controls, fg_color="transparent", height=34)
        filename_field.pack(fill="x", pady=(0, 8))
        filename_field.pack_propagate(False)
        self.filename_entry = ctk.CTkEntry(
            filename_field, textvariable=self.output_name, width=232
        )
        self.filename_entry.pack(fill="both", expand=True)
        self.filename_hint = ctk.CTkLabel(
            filename_field, text="Filename", text_color="gray55",
            cursor="xterm", fg_color="transparent"
        )
        self.filename_hint.place(x=12, rely=0.5, anchor="w")
        self.filename_hint.bind("<Button-1>", self._focus_filename_entry)
        self.filename_entry.bind("<FocusIn>", self._hide_filename_hint)
        self.filename_entry.bind("<FocusOut>", self._show_filename_hint)
        self.output_name.trace_add("write", self._update_filename_hint)
        export_buttons = ctk.CTkFrame(save_controls, fg_color="transparent")
        export_buttons.pack(fill="x")
        ctk.CTkButton(
            export_buttons, text="Copy", width=96, height=36,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.copy_rack
        ).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            export_buttons, text="Download", width=112, height=36,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent", hover_color=("gray85", "gray25"),
            border_width=1, border_color=("gray70", "gray40"),
            command=self.save_rack
        ).pack(side="left", fill="x", expand=True, padx=(8, 0))

        self.status_label = ctk.CTkLabel(
            footer, text="", wraplength=430, justify="left", anchor="w"
        )
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="ew", padx=12, pady=(5, 8))

    def _focus_filename_entry(self, _event):
        self.filename_entry.focus_set()
        self.filename_entry.icursor(0)

    def _hide_filename_hint(self, _event=None):
        self.filename_hint.place_forget()

    def _show_filename_hint(self, _event=None):
        if not self.output_name.get():
            self.filename_hint.place(x=12, rely=0.5, anchor="w")

    def _update_filename_hint(self, *_):
        if self.output_name.get():
            self._hide_filename_hint()
        else:
            self._show_filename_hint()

    def _add_ribbon_row(self, name):
        row = ctk.CTkFrame(self.ribbon_scroll)
        row.pack(fill="x", pady=2)
        checkbox = ctk.CTkCheckBox(
            row, text="", width=28, variable=self.ribbon_vars[name], command=self.redraw_preview
        )
        checkbox.pack(side="left", padx=(6, 0), pady=3)
        name_label = ctk.CTkLabel(
            row, text=name, anchor="w", cursor="hand2",
            font=ctk.CTkFont(size=13)
        )
        name_label.pack(side="left", fill="x", expand=True, padx=(0, 3), pady=3)
        name_label.bind("<Button-1>", lambda _event: checkbox.toggle())

        if name == "Legion of Merit":
            variants = [
                ribbon_name for ribbon_name, _, _, variant_of in RIBBON_TABLE
                if variant_of == name
            ]
            ctk.CTkOptionMenu(
                row,
                values=[name, *variants],
                variable=self.lom_variant, width=175,
                command=lambda _value: self.redraw_preview()
            ).pack(side="right", padx=5, pady=3)

        if name in DEVICE_CONFIG:
            _, device_count = DEVICE_CONFIG[name]
            ctk.CTkOptionMenu(
                row, values=[f"x{i}" for i in range(1, device_count + 1)],
                variable=self.device_vars[name], width=62,
                command=lambda _value: self.redraw_preview()
            ).pack(side="right", padx=5, pady=3)

    def precedence_key(self, name):
        base_name = "Legion of Merit" if name.startswith("Legion of Merit") else name
        return ORDER_OF_PRECEDENCE.get(base_name, len(RIBBON_NAMES) + 1)

    def active_ribbons(self):
        selected = []
        for name in RIBBON_NAMES:
            if self.ribbon_vars[name].get():
                selected.append(self.lom_variant.get() if name == "Legion of Merit" else name)
        return sorted(selected, key=self.precedence_key)

    @staticmethod
    def _image_size(scaled=False):
        width, height = CONFIG["ribbon_size"]
        scale = CONFIG["preview_scale"] if scaled else 1
        return width * scale, height * scale

    def _ribbon_image(self, name, scaled=False):
        cache = self.scaled_ribbon_cache if scaled else self.base_ribbon_cache
        if name in cache:
            return cache[name].copy()

        filename = RIBBON_FILES.get(name)
        size = self._image_size(scaled)
        if not filename:
            image = Image.new("RGBA", size, (0, 0, 0, 0))
        else:
            path = resource_path(os.path.join("Ribbons", filename))
            if os.path.isfile(path):
                try:
                    image = load_rgba(path, size)
                except (OSError, ValueError):
                    image = Image.new("RGBA", size, (110, 110, 110, 255))
            else:
                image = Image.new("RGBA", size, (110, 110, 110, 255))
        cache[name] = image
        return image.copy()

    def _device_image(self, folder, count, scaled=False):
        key = (folder, count, scaled)
        if key in self.device_cache:
            return self.device_cache[key].copy()
        size = self._image_size(scaled)
        path = resource_path(os.path.join("Devices", folder, f"{count}.png"))
        if not os.path.isfile(path):
            return None
        try:
            image = load_rgba(path, size)
        except (OSError, ValueError):
            return None
        self.device_cache[key] = image
        return image.copy()

    def _with_device(self, image, ribbon_name, scaled=False):
        lookup = "Legion of Merit" if ribbon_name.startswith("Legion of Merit") else ribbon_name
        config = DEVICE_CONFIG.get(lookup)
        if not config:
            return image
        count = self.device_vars[lookup].get()
        if count == "x1":
            return image
        overlay = self._device_image(config[0], count, scaled)
        if overlay is None:
            self.show_status(f"Missing device image: Devices/{config[0]}/{count}.png", error=True)
            return image
        image.alpha_composite(overlay)
        return image

    @staticmethod
    def _make_rows(ribbons, offset=False):
        per_row = CONFIG["ribbons_per_row"]
        if offset and len(ribbons) % per_row == 0:
            rows = [ribbons[:1], ribbons[1:per_row]]
            rows.extend(
                ribbons[i:i + per_row]
                for i in range(per_row, len(ribbons), per_row)
            )
            return rows
        if offset and len(ribbons) % per_row == 1 and len(ribbons) > 1:
            rows = [ribbons[:2], ribbons[2:4]]
            rows.extend(
                ribbons[i:i + per_row]
                for i in range(4, len(ribbons), per_row)
            )
            return rows

        top_row_size = len(ribbons) % per_row
        rows = [ribbons[:top_row_size]] if top_row_size else []
        rows.extend(
            ribbons[i:i + per_row]
            for i in range(top_row_size, len(ribbons), per_row)
        )
        return rows

    def build_rack_image(self, ribbons=None):
        ribbons = self.active_ribbons() if ribbons is None else ribbons
        if not ribbons:
            return None
        offset = self.offset_var.get()
        rows = self._make_rows(ribbons, offset=offset)
        ribbon_width, ribbon_height = self._image_size()
        rack = Image.new(
            "RGBA",
            (CONFIG["ribbons_per_row"] * ribbon_width, len(rows) * ribbon_height),
            (0, 0, 0, 0)
        )

        for row_index, row in enumerate(rows):
            row_width = len(row) * ribbon_width
            x_offset = (
                rack.width - row_width
                if offset else (rack.width - row_width) // 2
            )
            for col_index, name in enumerate(row):
                ribbon = self._with_device(self._ribbon_image(name), name)
                rack.alpha_composite(
                    ribbon, (x_offset + col_index * ribbon_width, row_index * ribbon_height)
                )
        return rack

    def redraw_preview(self):
        if not hasattr(self, "preview_canvas") or not self.preview_canvas.winfo_exists():
            return
        self.preview_canvas.delete("all")
        self.preview_photos.clear()
        ribbons = self.active_ribbons()
        self._sync_presets()
        self.selection_label.configure(
            text=f"{len(ribbons)} ribbon{'s' if len(ribbons) != 1 else ''} are currently selected"
        )
        if not ribbons:
            self.preview_canvas.create_text(
                max(1, self.preview_canvas.winfo_width()) // 2,
                max(1, self.preview_canvas.winfo_height()) // 2,
                text="Select at least one ribbon to see the preview.",
                fill="#888888", font=("Arial", 12)
            )
            return

        offset = self.offset_var.get()
        rows = self._make_rows(ribbons, offset=offset)
        canvas_width = max(self.preview_canvas.winfo_width(), 1)
        canvas_height = max(self.preview_canvas.winfo_height(), 1)
        ribbon_w, ribbon_h = self._image_size(scaled=True)
        rack_width = CONFIG["ribbons_per_row"] * ribbon_w
        rack_left = (canvas_width - rack_width) // 2
        rack_h = len(rows) * ribbon_h
        top = max(8, (canvas_height - rack_h) // 2)

        for row_index, row in enumerate(rows):
            row_width = len(row) * ribbon_w
            left = (
                rack_left + rack_width - row_width
                if offset else (canvas_width - row_width) // 2
            )
            for col_index, name in enumerate(row):
                image = self._with_device(self._ribbon_image(name, scaled=True), name, scaled=True)
                photo = ImageTk.PhotoImage(image)
                self.preview_photos.append(photo)
                self.preview_canvas.create_image(
                    left + col_index * ribbon_w, top + row_index * ribbon_h,
                    anchor="nw", image=photo
                )

    def _sync_presets(self):
        for name, ribbon_list in PRESETS.items():
            self.preset_vars[name].set(all(self.ribbon_vars[ribbon].get() for ribbon in ribbon_list))

    def select_all(self):
        for var in self.ribbon_vars.values():
            var.set(True)
        self.redraw_preview()

    def deselect_all(self):
        for var in self.ribbon_vars.values():
            var.set(False)
        self.redraw_preview()

    def reset_devices(self):
        for var in self.device_vars.values():
            var.set("x1")
        self.lom_variant.set("Legion of Merit")
        self.show_status("All devices and variants reset.")
        self.redraw_preview()

    def toggle_preset(self, preset_name):
        selected = self.preset_vars[preset_name].get()
        for ribbon in PRESETS[preset_name]:
            self.ribbon_vars[ribbon].set(selected)
        self.redraw_preview()

    def save_rack(self):
        rack = self.build_rack_image()
        if rack is None:
            self.show_status("Select at least one ribbon first.", error=True)
            return
        filename = f"{safe_filename(self.output_name.get(), 'Default')}_RibbonRack.png"
        try:
            rack.save(filename)
        except (OSError, ValueError) as exc:
            self.show_status(f"Could not save ribbon rack: {exc}", error=True)
            return

        path = os.path.abspath(filename)
        try:
            if sys.platform == "win32":
                os.startfile(path)
            else:
                self.show_status(f"Ribbon rack saved: {filename}")
                return
        except OSError as exc:
            self.show_status(f"Ribbon rack saved, but could not open it: {exc}", error=True)
            return
        self.show_status(f"Ribbon rack successfully saved: {filename}")

    def copy_rack(self):
        rack = self.build_rack_image()
        if rack is None:
            self.show_status("Select at least one ribbon first.", error=True)
            return
        try:
            self._copy_image_to_clipboard(rack)
            self.show_status("Copied ribbon rack to clipboard.")
        except (OSError, RuntimeError) as exc:
            self.show_status(f"Could not copy ribbon rack: {exc}", error=True)

    def _copy_image_to_clipboard(self, image):
        if os.name != "nt":
            raise RuntimeError("Image clipboard copying is only supported on Windows.")

        dib = self._dibv5_data(image)
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        user32.OpenClipboard.argtypes = [wintypes.HWND]
        user32.OpenClipboard.restype = wintypes.BOOL
        user32.EmptyClipboard.restype = wintypes.BOOL
        user32.SetClipboardData.argtypes = [wintypes.UINT, ctypes.c_void_p]
        user32.SetClipboardData.restype = ctypes.c_void_p
        user32.CloseClipboard.restype = wintypes.BOOL
        kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
        kernel32.GlobalAlloc.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        kernel32.GlobalUnlock.restype = wintypes.BOOL
        kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
        kernel32.GlobalFree.restype = ctypes.c_void_p

        memory = kernel32.GlobalAlloc(0x0002, len(dib))
        if not memory:
            raise ctypes.WinError(ctypes.get_last_error())
        locked = kernel32.GlobalLock(memory)
        if not locked:
            error = ctypes.get_last_error()
            kernel32.GlobalFree(memory)
            raise ctypes.WinError(error)
        ctypes.memmove(locked, dib, len(dib))
        kernel32.GlobalUnlock(memory)

        if not user32.OpenClipboard(self.root.winfo_id()):
            error = ctypes.get_last_error()
            kernel32.GlobalFree(memory)
            raise ctypes.WinError(error)
        try:
            if not user32.EmptyClipboard():
                raise ctypes.WinError(ctypes.get_last_error())
            if not user32.SetClipboardData(17, memory):
                raise ctypes.WinError(ctypes.get_last_error())
            memory = None
        finally:
            user32.CloseClipboard()
            if memory:
                kernel32.GlobalFree(memory)

    @staticmethod
    def _dibv5_data(image):
        width, height = image.size
        pixels = image.convert("RGBA").tobytes("raw", "BGRA")
        header = struct.pack(
            "<IiiHHIIiiII",
            124, width, -height, 1, 32, 3, len(pixels), 0, 0, 0, 0
        )
        masks = struct.pack("<IIII", 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
        return header + masks + struct.pack("<I", 0x73524742) + bytes(64) + pixels

    def show_status(self, message, error=False):
        if self.status_after_id is not None:
            try:
                self.root.after_cancel(self.status_after_id)
            except tk.TclError:
                pass
            self.status_after_id = None
        self.status_label.configure(text=message, text_color="#ff5c5c" if error else "#69d17d")
        self.status_after_id = self.root.after(5000, self._clear_status)

    def _clear_status(self):
        self.status_after_id = None
        if self.status_label.winfo_exists():
            self.status_label.configure(text="")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    RibbonRackBuilder().run()
