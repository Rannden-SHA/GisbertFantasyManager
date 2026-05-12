"""
KPI / Statistic card widget for Gisbert's Fantasy Manager v2.0
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing


class StatCard(ctk.CTkFrame):
    """A beautiful KPI card showing a metric with icon, value, and optional delta."""

    def __init__(self, parent, title: str = "", value: str = "", icon: str = "",
                 accent_color: str = Colors.ACCENT_BLUE, delta: str = "",
                 delta_positive: bool = True, subtitle: str = "", **kwargs):
        super().__init__(parent, corner_radius=14, fg_color=Colors.BG_CARD,
                         border_width=1, border_color=Colors.BORDER, **kwargs)

        self.accent_color = accent_color
        self._build(title, value, icon, delta, delta_positive, subtitle)

    def _build(self, title, value, icon, delta, delta_positive, subtitle):
        # Main container with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.MD)

        # Top row: icon + title
        top_row = ctk.CTkFrame(container, fg_color="transparent")
        top_row.pack(fill="x")

        if icon:
            icon_bg = ctk.CTkFrame(top_row, width=36, height=36, corner_radius=10,
                                    fg_color=self._get_muted_color())
            icon_bg.pack(side="left")
            icon_bg.pack_propagate(False)
            icon_label = ctk.CTkLabel(icon_bg, text=icon, font=("Segoe UI Emoji", 16))
            icon_label.place(relx=0.5, rely=0.5, anchor="center")

        title_label = ctk.CTkLabel(
            top_row, text=title,
            font=Fonts.BODY_XS,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        )
        title_label.pack(side="left", padx=(Spacing.SM if icon else 0, 0))

        # Value
        self.value_label = ctk.CTkLabel(
            container, text=value,
            font=Fonts.MONO_LG,
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        self.value_label.pack(fill="x", pady=(Spacing.SM, 0))

        # Bottom row: delta or subtitle
        if delta or subtitle:
            bottom_row = ctk.CTkFrame(container, fg_color="transparent")
            bottom_row.pack(fill="x", pady=(Spacing.XS, 0))

            if delta:
                delta_color = Colors.ACCENT_GREEN if delta_positive else Colors.ACCENT_RED
                delta_icon = "▲" if delta_positive else "▼"
                delta_label = ctk.CTkLabel(
                    bottom_row, text=f"{delta_icon} {delta}",
                    font=Fonts.CAPTION,
                    text_color=delta_color,
                    anchor="w"
                )
                delta_label.pack(side="left")

            if subtitle:
                sub_label = ctk.CTkLabel(
                    bottom_row, text=subtitle,
                    font=Fonts.CAPTION,
                    text_color=Colors.TEXT_MUTED,
                    anchor="w"
                )
                sub_label.pack(side="left", padx=(Spacing.SM if delta else 0, 0))

    def _get_muted_color(self) -> str:
        """Get a muted version of the accent color for the icon background."""
        # Simple approach: darken the accent
        return Colors.BG_TERTIARY

    def update_value(self, new_value: str):
        """Update the displayed value."""
        self.value_label.configure(text=new_value)
