"""
Sortable data table widget for Gisbert's Fantasy Manager v2.0
Built with CustomTkinter for a modern dark theme look.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing


class DataTable(ctk.CTkFrame):
    """A modern sortable data table widget."""

    def __init__(self, parent, columns: list, data: list = None,
                 title: str = "", row_height: int = 38, **kwargs):
        """
        Args:
            parent: Parent widget
            columns: List of dicts with keys: 'key', 'label', 'width' (optional), 'align' (optional)
            data: List of dicts with keys matching column keys
            title: Optional table title
            row_height: Height of each row
        """
        super().__init__(parent, corner_radius=14, fg_color=Colors.BG_CARD,
                         border_width=1, border_color=Colors.BORDER, **kwargs)
        self.columns = columns
        self.data = data or []
        self.row_height = row_height
        self.sort_column = None
        self.sort_ascending = True
        self.row_widgets = []

        self._build(title)

    def _build(self, title):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)

        # Title
        if title:
            title_frame = ctk.CTkFrame(container, fg_color="transparent")
            title_frame.pack(fill="x", pady=(0, Spacing.MD))
            ctk.CTkLabel(
                title_frame, text=title,
                font=Fonts.TITLE_SM,
                text_color=Colors.TEXT_PRIMARY
            ).pack(side="left")

        # Header row
        header_frame = ctk.CTkFrame(container, fg_color=Colors.BG_TERTIARY,
                                     corner_radius=8, height=36)
        header_frame.pack(fill="x", pady=(0, 2))
        header_frame.pack_propagate(False)

        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="both", expand=True, padx=Spacing.SM)

        for i, col in enumerate(self.columns):
            weight = col.get("weight", 1)
            header_inner.grid_columnconfigure(i, weight=weight)
            
            lbl = ctk.CTkLabel(
                header_inner, text=col["label"],
                font=Fonts.BODY_XS,
                text_color=Colors.TEXT_MUTED,
                anchor=col.get("align", "w")
            )
            lbl.grid(row=0, column=i, sticky="ew", padx=Spacing.SM, pady=6)
            lbl.bind("<Button-1>", lambda e, key=col["key"]: self._sort_by(key))

        # Scrollable body
        self.body_frame = ctk.CTkScrollableFrame(
            container, fg_color="transparent",
            scrollbar_button_color=Colors.BG_TERTIARY,
            scrollbar_button_hover_color=Colors.BG_HOVER
        )
        self.body_frame.pack(fill="both", expand=True)

        # Render data
        self._render_rows()

    def _render_rows(self):
        # Clear existing
        for widget in self.body_frame.winfo_children():
            widget.destroy()
        self.row_widgets = []

        if not self.data:
            empty_label = ctk.CTkLabel(
                self.body_frame, text="Sin datos disponibles",
                font=Fonts.BODY_SM,
                text_color=Colors.TEXT_MUTED
            )
            empty_label.pack(pady=Spacing.XL)
            return

        for row_idx, row_data in enumerate(self.data):
            bg = "transparent" if row_idx % 2 == 0 else Colors.BG_SECONDARY
            row_frame = ctk.CTkFrame(self.body_frame, fg_color=bg,
                                      corner_radius=6, height=self.row_height)
            row_frame.pack(fill="x", pady=1)
            row_frame.pack_propagate(False)

            row_inner = ctk.CTkFrame(row_frame, fg_color="transparent")
            row_inner.pack(fill="both", expand=True, padx=Spacing.SM)

            for i, col in enumerate(self.columns):
                weight = col.get("weight", 1)
                row_inner.grid_columnconfigure(i, weight=weight)

                value = row_data.get(col["key"], "")
                color = row_data.get(f"{col['key']}_color", Colors.TEXT_PRIMARY)

                lbl = ctk.CTkLabel(
                    row_inner, text=str(value),
                    font=Fonts.BODY_SM,
                    text_color=color,
                    anchor=col.get("align", "w")
                )
                lbl.grid(row=0, column=i, sticky="ew", padx=Spacing.SM, pady=6)

            # Hover effect
            for widget in [row_frame, row_inner] + list(row_inner.winfo_children()):
                widget.bind("<Enter>", lambda e, rf=row_frame: rf.configure(fg_color=Colors.BG_HOVER))
                widget.bind("<Leave>", lambda e, rf=row_frame, b=bg: rf.configure(fg_color=b))

            self.row_widgets.append(row_frame)

    def _sort_by(self, key: str):
        if self.sort_column == key:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = key
            self.sort_ascending = True

        try:
            self.data.sort(key=lambda x: x.get(key, ""), reverse=not self.sort_ascending)
        except TypeError:
            self.data.sort(key=lambda x: str(x.get(key, "")), reverse=not self.sort_ascending)
        self._render_rows()

    def update_data(self, new_data: list):
        """Replace table data and re-render."""
        self.data = new_data
        self._render_rows()
