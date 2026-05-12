"""
Modern sidebar navigation widget for Gisbert's Fantasy Manager v2.0
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing, NAV_ITEMS, SIDEBAR_WIDTH


class Sidebar(ctk.CTkFrame):
    """Dark sidebar navigation with icon + label navigation items."""

    def __init__(self, parent, on_navigate, **kwargs):
        super().__init__(parent, width=SIDEBAR_WIDTH, corner_radius=0,
                         fg_color=Colors.BG_SECONDARY, **kwargs)
        self.on_navigate = on_navigate
        self.active_item = "dashboard"
        self.nav_buttons = {}
        self.pack_propagate(False)

        self._build_header()
        self._build_nav()
        self._build_footer()

    def _build_header(self):
        """Build the logo/brand header area."""
        header = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header.pack(fill="x", padx=Spacing.MD, pady=(Spacing.LG, Spacing.SM))
        header.pack_propagate(False)

        # Brand icon circle
        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.pack(expand=True)

        icon_label = ctk.CTkLabel(
            brand_frame, text="⚽",
            font=("Segoe UI Emoji", 28),
            text_color=Colors.ACCENT_BLUE
        )
        icon_label.pack()

        title = ctk.CTkLabel(
            brand_frame, text="GFM",
            font=Fonts.TITLE_SM,
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            brand_frame, text="Fantasy Manager",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_MUTED
        )
        subtitle.pack()

        # Separator
        sep = ctk.CTkFrame(self, fg_color=Colors.BORDER, height=1)
        sep.pack(fill="x", padx=Spacing.LG, pady=(Spacing.SM, Spacing.MD))

    def _build_nav(self):
        """Build navigation items."""
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=Spacing.SM)

        for item in NAV_ITEMS:
            btn = self._create_nav_button(nav_frame, item)
            self.nav_buttons[item["id"]] = btn

        # Set initial active
        self._set_active("dashboard")

    def _create_nav_button(self, parent, item):
        """Create a single navigation button."""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent", height=42, corner_radius=10)
        btn_frame.pack(fill="x", pady=2)
        btn_frame.pack_propagate(False)

        inner = ctk.CTkFrame(btn_frame, fg_color="transparent", corner_radius=10)
        inner.pack(fill="both", expand=True, padx=4, pady=1)

        content = ctk.CTkFrame(inner, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=Spacing.MD)

        # Use a single row with icon + label
        content.grid_columnconfigure(1, weight=1)

        icon_lbl = ctk.CTkLabel(
            content, text=item["icon"],
            font=("Segoe UI Emoji", 16),
            width=28, anchor="w"
        )
        icon_lbl.grid(row=0, column=0, sticky="w", pady=8)

        text_lbl = ctk.CTkLabel(
            content, text=item["label"],
            font=Fonts.BODY_SM,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        )
        text_lbl.grid(row=0, column=1, sticky="w", padx=(4, 0), pady=8)

        # Click bindings
        for widget in [btn_frame, inner, content, icon_lbl, text_lbl]:
            widget.bind("<Button-1>", lambda e, item_id=item["id"]: self._on_click(item_id))
            widget.bind("<Enter>", lambda e, bf=inner: self._on_enter(bf))
            widget.bind("<Leave>", lambda e, bf=inner, item_id=item["id"]: self._on_leave(bf, item_id))

        return {
            "frame": inner,
            "icon": icon_lbl,
            "text": text_lbl,
        }

    def _on_click(self, item_id: str):
        self._set_active(item_id)
        self.on_navigate(item_id)

    def _set_active(self, item_id: str):
        # Deactivate previous
        if self.active_item in self.nav_buttons:
            prev = self.nav_buttons[self.active_item]
            prev["frame"].configure(fg_color="transparent")
            prev["text"].configure(text_color=Colors.TEXT_SECONDARY)

        # Activate new
        self.active_item = item_id
        if item_id in self.nav_buttons:
            curr = self.nav_buttons[item_id]
            curr["frame"].configure(fg_color=Colors.BG_TERTIARY)
            curr["text"].configure(text_color=Colors.TEXT_PRIMARY)

    def _on_enter(self, frame):
        if frame.cget("fg_color") != Colors.BG_TERTIARY:
            frame.configure(fg_color=Colors.BG_HOVER)

    def _on_leave(self, frame, item_id):
        if item_id != self.active_item:
            frame.configure(fg_color="transparent")

    def _build_footer(self):
        """Build the sidebar footer."""
        sep = ctk.CTkFrame(self, fg_color=Colors.BORDER, height=1)
        sep.pack(fill="x", padx=Spacing.LG, pady=(Spacing.SM, Spacing.SM))

        footer = ctk.CTkFrame(self, fg_color="transparent", height=40)
        footer.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.MD))

        version_label = ctk.CTkLabel(
            footer, text="v2.0 • Gisbert",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_MUTED
        )
        version_label.pack()

    def navigate_to(self, item_id: str):
        """Programmatically navigate to a section."""
        self._set_active(item_id)
        self.on_navigate(item_id)
