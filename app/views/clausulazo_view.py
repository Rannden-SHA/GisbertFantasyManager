"""
Clausulazo calculator view.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing
from utils import calculate_clausula, format_money


class ClausulazoView(ctk.CTkFrame):
    def __init__(self, parent, db, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                         scrollbar_button_color=Colors.BG_TERTIARY,
                                         scrollbar_button_hover_color=Colors.BG_HOVER)
        scroll.pack(fill="both", expand=True)

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.MD))
        ctk.CTkLabel(header, text="💰 Calculadora de Clausulazo", font=Fonts.TITLE_LG,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left")

        # Rules explanation
        rules_card = ctk.CTkFrame(scroll, corner_radius=14, fg_color=Colors.BG_CARD,
                                   border_width=1, border_color=Colors.BORDER)
        rules_card.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))
        rules_inner = ctk.CTkFrame(rules_card, fg_color="transparent")
        rules_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(rules_inner, text="📖 Reglas del Clausulazo", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.SM))

        rules = [
            ("Valor < 1.000.000€", "Cláusula = 1.000.000€ (fija)", Colors.ACCENT_ORANGE),
            ("Valor ≥ 1.000.000€", "Cláusula = 66% del valor de mercado", Colors.ACCENT_BLUE),
            ("⚡ Ventaja", "No necesitas la aceptación del otro mánager", Colors.ACCENT_GREEN),
        ]
        for title, desc, color in rules:
            rule_row = ctk.CTkFrame(rules_inner, fg_color=Colors.BG_TERTIARY, corner_radius=8)
            rule_row.pack(fill="x", pady=2)
            rule_inner = ctk.CTkFrame(rule_row, fg_color="transparent")
            rule_inner.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)
            ctk.CTkLabel(rule_inner, text=title, font=Fonts.BODY_SM,
                          text_color=color).pack(side="left")
            ctk.CTkLabel(rule_inner, text=desc, font=Fonts.BODY_XS,
                          text_color=Colors.TEXT_SECONDARY).pack(side="right")

        # Calculator
        calc_card = ctk.CTkFrame(scroll, corner_radius=14, fg_color=Colors.BG_CARD,
                                  border_width=1, border_color=Colors.BORDER)
        calc_card.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))

        calc_inner = ctk.CTkFrame(calc_card, fg_color="transparent")
        calc_inner.pack(fill="both", padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(calc_inner, text="🧮 Calcular", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.MD))

        # Input
        input_frame = ctk.CTkFrame(calc_inner, fg_color="transparent")
        input_frame.pack(fill="x")

        ctk.CTkLabel(input_frame, text="Valor de Mercado del Jugador (€)",
                      font=Fonts.BODY_XS, text_color=Colors.TEXT_SECONDARY).pack(anchor="w")
        self.value_entry = ctk.CTkEntry(input_frame, placeholder_text="Ej: 5000000",
                                         font=Fonts.MONO_MD, height=48, corner_radius=10,
                                         fg_color=Colors.BG_TERTIARY, border_color=Colors.ACCENT_BLUE,
                                         text_color=Colors.TEXT_PRIMARY, border_width=2)
        self.value_entry.pack(fill="x", pady=(4, Spacing.MD))
        self.value_entry.bind("<KeyRelease>", lambda e: self._calculate())

        # Participant selector for affordability check
        participants = self.db.get_participants()
        if participants:
            ctk.CTkLabel(input_frame, text="Verificar con participante (opcional)",
                          font=Fonts.BODY_XS, text_color=Colors.TEXT_SECONDARY).pack(anchor="w")
            p_names = ["(ninguno)"] + [p.name for p in participants]
            self.participant_dd = ctk.CTkComboBox(input_frame, values=p_names,
                                                    font=Fonts.BODY, height=36, corner_radius=8,
                                                    fg_color=Colors.BG_TERTIARY, border_color=Colors.BORDER,
                                                    text_color=Colors.TEXT_PRIMARY, border_width=1,
                                                    button_color=Colors.ACCENT_BLUE,
                                                    dropdown_fg_color=Colors.BG_TERTIARY,
                                                    dropdown_text_color=Colors.TEXT_PRIMARY,
                                                    command=lambda v: self._calculate())
            self.participant_dd.pack(fill="x", pady=(4, Spacing.MD))
            self.participant_dd.set("(ninguno)")
        else:
            self.participant_dd = None

        # Results
        self.result_frame = ctk.CTkFrame(calc_inner, fg_color=Colors.BG_TERTIARY, corner_radius=10)
        self.result_frame.pack(fill="x")
        self.result_label = ctk.CTkLabel(self.result_frame, text="Introduce un valor de mercado...",
                                          font=Fonts.BODY, text_color=Colors.TEXT_MUTED)
        self.result_label.pack(padx=Spacing.LG, pady=Spacing.LG)

        # Quick presets
        presets_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        presets_frame.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))

        ctk.CTkLabel(presets_frame, text="⚡ Cálculo Rápido", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.SM))

        presets = ctk.CTkFrame(presets_frame, fg_color="transparent")
        presets.pack(fill="x")

        preset_values = [500_000, 1_000_000, 3_000_000, 5_000_000,
                         10_000_000, 15_000_000, 20_000_000, 30_000_000]
        cols = 4
        for i in range(cols):
            presets.grid_columnconfigure(i, weight=1)

        for i, val in enumerate(preset_values):
            clausula = calculate_clausula(val)
            card = ctk.CTkFrame(presets, corner_radius=10, fg_color=Colors.BG_CARD,
                                 border_width=1, border_color=Colors.BORDER)
            card.grid(row=i // cols, column=i % cols, sticky="nsew", padx=4, pady=4)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=Spacing.MD, pady=Spacing.SM)
            ctk.CTkLabel(inner, text=format_money(val, True), font=Fonts.BODY_SM,
                          text_color=Colors.TEXT_SECONDARY).pack()
            ctk.CTkLabel(inner, text=f"→ {format_money(clausula, True)}", font=Fonts.MONO_SM,
                          text_color=Colors.ACCENT_BLUE).pack()
            pct = (clausula / val * 100) if val > 0 else 0
            ctk.CTkLabel(inner, text=f"({pct:.0f}%)", font=Fonts.CAPTION,
                          text_color=Colors.TEXT_MUTED).pack()

    def _calculate(self):
        try:
            value_str = self.value_entry.get().replace(".", "").replace(",", "").strip()
            if not value_str:
                self.result_label.configure(text="Introduce un valor de mercado...",
                                             text_color=Colors.TEXT_MUTED)
                return
            market_value = float(value_str)
            clausula = calculate_clausula(market_value)

            # Destroy old result and rebuild
            for w in self.result_frame.winfo_children():
                w.destroy()

            inner = ctk.CTkFrame(self.result_frame, fg_color="transparent")
            inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)

            ctk.CTkLabel(inner, text="Valor de Mercado", font=Fonts.BODY_XS,
                          text_color=Colors.TEXT_MUTED).pack(anchor="w")
            ctk.CTkLabel(inner, text=format_money(market_value), font=Fonts.MONO_MD,
                          text_color=Colors.TEXT_PRIMARY).pack(anchor="w")

            ctk.CTkLabel(inner, text="Precio del Clausulazo", font=Fonts.BODY_XS,
                          text_color=Colors.ACCENT_BLUE).pack(anchor="w", pady=(Spacing.SM, 0))
            ctk.CTkLabel(inner, text=format_money(clausula), font=Fonts.MONO_LG,
                          text_color=Colors.ACCENT_BLUE).pack(anchor="w")

            savings = market_value - clausula
            if savings > 0:
                ctk.CTkLabel(inner, text=f"💡 Ahorras {format_money(savings, True)} vs. valor de mercado",
                              font=Fonts.BODY_SM, text_color=Colors.ACCENT_GREEN).pack(anchor="w", pady=(Spacing.SM, 0))

            # Affordability check
            if self.participant_dd and self.participant_dd.get() != "(ninguno)":
                p = self.db.get_participant(self.participant_dd.get())
                if p:
                    can_afford = p.max_bid >= clausula
                    color = Colors.ACCENT_GREEN if can_afford else Colors.ACCENT_RED
                    status = "✅ ¡Puedes permitirte este clausulazo!" if can_afford \
                        else "❌ No tienes suficiente puja máxima"
                    ctk.CTkLabel(inner, text=status, font=Fonts.BODY_SM,
                                  text_color=color).pack(anchor="w", pady=(Spacing.SM, 0))
                    ctk.CTkLabel(inner, text=f"Tu puja máxima: {format_money(p.max_bid, True)}",
                                  font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED).pack(anchor="w")

        except (ValueError, TypeError):
            self.result_label.configure(text="Valor no válido", text_color=Colors.ACCENT_RED)

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
