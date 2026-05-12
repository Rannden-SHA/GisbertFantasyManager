"""
Transaction form widget for Gisbert's Fantasy Manager v2.0
Unified form for buy/sell/money/points operations.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing


class TransactionForm(ctk.CTkFrame):
    """Inline form for registering transactions with live preview."""

    def __init__(self, parent, participants: list, on_submit=None, form_type="purchase", **kwargs):
        super().__init__(parent, corner_radius=14, fg_color=Colors.BG_CARD,
                         border_width=1, border_color=Colors.BORDER, **kwargs)
        self.on_submit = on_submit
        self.participants = participants
        self.form_type = form_type
        self.entries = {}
        self._build()

    def _build(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)

        # Form type tabs
        tabs = ctk.CTkFrame(container, fg_color="transparent")
        tabs.pack(fill="x", pady=(0, Spacing.MD))
        types = [
            ("purchase", "🛒 Compra", Colors.ACCENT_GREEN),
            ("sale", "💰 Venta", Colors.ACCENT_ORANGE),
            ("money", "💵 Dinero", Colors.ACCENT_BLUE),
            ("points", "⭐ Puntos", Colors.ACCENT_PURPLE),
            ("team_value", "📊 Valor Equipo", Colors.ACCENT_CYAN),
        ]
        self.tab_buttons = {}
        for tid, label, color in types:
            btn = ctk.CTkButton(tabs, text=label, font=Fonts.BODY_XS, height=32, corner_radius=8,
                                 fg_color=Colors.BG_TERTIARY if tid != self.form_type else color,
                                 hover_color=color, text_color=Colors.TEXT_PRIMARY,
                                 command=lambda t=tid: self._switch_type(t))
            btn.pack(side="left", padx=2)
            self.tab_buttons[tid] = (btn, color)

        # Fields container
        self.fields_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.fields_frame.pack(fill="x")

        self._build_fields()

        # Preview + Submit
        self.preview_frame = ctk.CTkFrame(container, fg_color=Colors.BG_TERTIARY, corner_radius=10)
        self.preview_frame.pack(fill="x", pady=(Spacing.MD, 0))
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="Vista previa del resultado...",
                                           font=Fonts.BODY_SM, text_color=Colors.TEXT_MUTED)
        self.preview_label.pack(padx=Spacing.MD, pady=Spacing.SM)

        submit_btn = ctk.CTkButton(container, text="✓ Confirmar Operación", font=Fonts.BODY,
                                    height=40, corner_radius=10, fg_color=Colors.ACCENT_BLUE,
                                    hover_color=Colors.ACCENT_BLUE_HOVER, command=self._submit)
        submit_btn.pack(fill="x", pady=(Spacing.MD, 0))

    def _build_fields(self):
        for w in self.fields_frame.winfo_children():
            w.destroy()
        self.entries = {}

        # Participant selector (always)
        self._add_dropdown("participant", "Participante", self.participants)

        if self.form_type == "purchase":
            self._add_entry("player_name", "Nombre del Jugador")
            self._add_entry("market_value", "Valor de Mercado (€)", numeric=True)
            self._add_entry("amount", "Precio de Compra (€)", numeric=True)
        elif self.form_type == "sale":
            self._add_entry("player_name", "Nombre del Jugador")
            self._add_entry("amount", "Precio de Venta (€)", numeric=True)
        elif self.form_type == "money":
            self._add_entry("amount", "Cantidad (€)", numeric=True)
        elif self.form_type == "points":
            self._add_entry("points", "Puntos Obtenidos", numeric=True)
        elif self.form_type == "team_value":
            self._add_entry("amount", "Nuevo Valor del Equipo (€)", numeric=True)

    def _add_entry(self, key, label, numeric=False):
        frame = ctk.CTkFrame(self.fields_frame, fg_color="transparent")
        frame.pack(fill="x", pady=(0, Spacing.SM))
        ctk.CTkLabel(frame, text=label, font=Fonts.BODY_XS,
                      text_color=Colors.TEXT_SECONDARY).pack(anchor="w")
        entry = ctk.CTkEntry(frame, font=Fonts.BODY, height=36, corner_radius=8,
                              fg_color=Colors.BG_TERTIARY, border_color=Colors.BORDER,
                              text_color=Colors.TEXT_PRIMARY, border_width=1)
        entry.pack(fill="x", pady=(2, 0))
        entry.bind("<KeyRelease>", lambda e: self._update_preview())
        self.entries[key] = entry

    def _add_dropdown(self, key, label, values):
        frame = ctk.CTkFrame(self.fields_frame, fg_color="transparent")
        frame.pack(fill="x", pady=(0, Spacing.SM))
        ctk.CTkLabel(frame, text=label, font=Fonts.BODY_XS,
                      text_color=Colors.TEXT_SECONDARY).pack(anchor="w")
        dropdown = ctk.CTkComboBox(frame, values=values if values else ["(sin participantes)"],
                                    font=Fonts.BODY, height=36, corner_radius=8,
                                    fg_color=Colors.BG_TERTIARY, border_color=Colors.BORDER,
                                    text_color=Colors.TEXT_PRIMARY, border_width=1,
                                    button_color=Colors.ACCENT_BLUE,
                                    dropdown_fg_color=Colors.BG_TERTIARY,
                                    dropdown_text_color=Colors.TEXT_PRIMARY,
                                    dropdown_hover_color=Colors.BG_HOVER)
        dropdown.pack(fill="x", pady=(2, 0))
        if values:
            dropdown.set(values[0])
        self.entries[key] = dropdown

    def _switch_type(self, new_type):
        # Update tab styles
        for tid, (btn, color) in self.tab_buttons.items():
            btn.configure(fg_color=color if tid == new_type else Colors.BG_TERTIARY)
        self.form_type = new_type
        self._build_fields()
        self._update_preview()

    def _update_preview(self):
        try:
            data = self.get_data()
            participant = data.get("participant", "?")
            if self.form_type == "purchase":
                amt = float(data.get("amount", 0) or 0)
                player = data.get("player_name", "?")
                self.preview_label.configure(
                    text=f"{participant} compra a {player} por {amt:,.0f}€",
                    text_color=Colors.ACCENT_GREEN)
            elif self.form_type == "sale":
                amt = float(data.get("amount", 0) or 0)
                player = data.get("player_name", "?")
                self.preview_label.configure(
                    text=f"{participant} vende a {player} por {amt:,.0f}€",
                    text_color=Colors.ACCENT_ORANGE)
            elif self.form_type == "money":
                amt = float(data.get("amount", 0) or 0)
                self.preview_label.configure(
                    text=f"Se añaden {amt:,.0f}€ a {participant}",
                    text_color=Colors.ACCENT_BLUE)
            elif self.form_type == "points":
                pts = int(float(data.get("points", 0) or 0))
                money = pts * 100_000
                self.preview_label.configure(
                    text=f"{participant} recibe {pts} pts → +{money:,.0f}€",
                    text_color=Colors.ACCENT_PURPLE)
            elif self.form_type == "team_value":
                amt = float(data.get("amount", 0) or 0)
                self.preview_label.configure(
                    text=f"Valor equipo de {participant} → {amt:,.0f}€",
                    text_color=Colors.ACCENT_CYAN)
        except (ValueError, TypeError):
            self.preview_label.configure(text="Completa los campos...", text_color=Colors.TEXT_MUTED)

    def get_data(self) -> dict:
        data = {"type": self.form_type}
        for key, widget in self.entries.items():
            if isinstance(widget, ctk.CTkComboBox):
                data[key] = widget.get()
            else:
                data[key] = widget.get()
        return data

    def _submit(self):
        if self.on_submit:
            self.on_submit(self.get_data())

    def clear(self):
        for key, widget in self.entries.items():
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")

    def update_participants(self, participants: list):
        self.participants = participants
        self._build_fields()
