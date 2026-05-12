"""
Search bar widget for Gisbert's Fantasy Manager v2.0
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing


class SearchBar(ctk.CTkFrame):
    def __init__(self, parent, placeholder="Buscar...", on_search=None, filters=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.on_search = on_search
        self.active_filter = None
        self.filter_buttons = {}
        self._build(placeholder, filters)

    def _build(self, placeholder, filters):
        search_frame = ctk.CTkFrame(self, fg_color=Colors.BG_TERTIARY, corner_radius=10, height=40)
        search_frame.pack(side="left", fill="x", expand=True)
        search_frame.pack_propagate(False)
        inner = ctk.CTkFrame(search_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=Spacing.MD)
        ctk.CTkLabel(inner, text="🔍", font=("Segoe UI Emoji", 14), width=24).pack(side="left")
        self.entry = ctk.CTkEntry(inner, placeholder_text=placeholder, font=Fonts.BODY_SM,
                                   fg_color="transparent", border_width=0,
                                   text_color=Colors.TEXT_PRIMARY,
                                   placeholder_text_color=Colors.TEXT_MUTED)
        self.entry.pack(side="left", fill="x", expand=True, padx=(4, 0))
        self.entry.bind("<Return>", self._on_search_event)
        self.entry.bind("<KeyRelease>", self._on_search_event)
        ctk.CTkButton(inner, text="✕", width=24, height=24, font=Fonts.BODY_SM,
                       fg_color="transparent", hover_color=Colors.BG_HOVER,
                       text_color=Colors.TEXT_MUTED, command=self._clear).pack(side="right")
        if filters:
            ff = ctk.CTkFrame(self, fg_color="transparent")
            ff.pack(side="left", padx=(8, 0))
            for f in filters:
                btn = ctk.CTkButton(ff, text=f["label"], font=Fonts.BODY_XS, width=70, height=32,
                                     corner_radius=8, fg_color=Colors.BG_TERTIARY,
                                     hover_color=Colors.BG_HOVER, text_color=Colors.TEXT_SECONDARY,
                                     command=lambda fid=f["id"]: self._toggle_filter(fid))
                btn.pack(side="left", padx=2)
                self.filter_buttons[f["id"]] = btn

    def _on_search_event(self, event=None):
        if self.on_search:
            self.on_search(self.entry.get(), self.active_filter)

    def _clear(self):
        self.entry.delete(0, "end")
        self._on_search_event()

    def _toggle_filter(self, fid):
        if self.active_filter == fid:
            self.active_filter = None
            self.filter_buttons[fid].configure(fg_color=Colors.BG_TERTIARY, text_color=Colors.TEXT_SECONDARY)
        else:
            if self.active_filter and self.active_filter in self.filter_buttons:
                self.filter_buttons[self.active_filter].configure(fg_color=Colors.BG_TERTIARY, text_color=Colors.TEXT_SECONDARY)
            self.active_filter = fid
            self.filter_buttons[fid].configure(fg_color=Colors.ACCENT_BLUE, text_color=Colors.TEXT_PRIMARY)
        self._on_search_event()

    def get_value(self):
        return self.entry.get()
