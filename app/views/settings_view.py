"""
Settings view for league config, theme, and data management.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing
from models import LeagueConfig, Participant


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, db, on_refresh=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.db = db
        self.on_refresh = on_refresh
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                         scrollbar_button_color=Colors.BG_TERTIARY,
                                         scrollbar_button_hover_color=Colors.BG_HOVER)
        scroll.pack(fill="both", expand=True)

        header = ctk.CTkFrame(scroll, fg_color="transparent")
        header.pack(fill="x", padx=Spacing.LG, pady=(Spacing.LG, Spacing.MD))
        ctk.CTkLabel(header, text="⚙️ Ajustes de Liga", font=Fonts.TITLE_LG,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left")

        config = self.db.get_config()

        # League info card
        info_card = ctk.CTkFrame(scroll, corner_radius=14, fg_color=Colors.BG_CARD,
                                  border_width=1, border_color=Colors.BORDER)
        info_card.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))
        info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        info_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(info_inner, text="📋 Información de Liga", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.MD))

        if config:
            self._add_info_row(info_inner, "Nombre", config.name)
            self._add_info_row(info_inner, "Creada", config.created_at[:10] if config.created_at else "—")
            from utils import format_money
            self._add_info_row(info_inner, "Presupuesto inicial", format_money(config.initial_budget))
            self._add_info_row(info_inner, "Multiplicador de puntos", f"×{config.points_multiplier:,.0f}€")
            self._add_info_row(info_inner, "% Puja máxima", f"{config.max_bid_percent * 100:.0f}%")
            self._add_info_row(info_inner, "Jornada actual", str(config.current_jornada))

        # Participants management
        part_card = ctk.CTkFrame(scroll, corner_radius=14, fg_color=Colors.BG_CARD,
                                  border_width=1, border_color=Colors.BORDER)
        part_card.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))
        part_inner = ctk.CTkFrame(part_card, fg_color="transparent")
        part_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)

        top_row = ctk.CTkFrame(part_inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, Spacing.MD))
        ctk.CTkLabel(top_row, text="👥 Participantes", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(top_row, text="+ Añadir", font=Fonts.BODY_SM, height=32,
                       corner_radius=8, fg_color=Colors.ACCENT_BLUE,
                       hover_color=Colors.ACCENT_BLUE_HOVER,
                       command=self._add_participant).pack(side="right")

        participants = self.db.get_participants()
        for p in participants:
            row = ctk.CTkFrame(part_inner, fg_color=Colors.BG_TERTIARY, corner_radius=8)
            row.pack(fill="x", pady=2)
            row_inner = ctk.CTkFrame(row, fg_color="transparent")
            row_inner.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)

            avatar = ctk.CTkFrame(row_inner, width=28, height=28, corner_radius=14,
                                   fg_color=p.avatar_color)
            avatar.pack(side="left")
            avatar.pack_propagate(False)
            initials = "".join(w[0].upper() for w in p.name.split()[:2])
            ctk.CTkLabel(avatar, text=initials, font=Fonts.CAPTION,
                          text_color=Colors.TEXT_PRIMARY).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(row_inner, text=p.name, font=Fonts.BODY_SM,
                          text_color=Colors.TEXT_PRIMARY).pack(side="left", padx=(Spacing.SM, 0))

            ctk.CTkButton(row_inner, text="🗑", width=28, height=28, font=("Segoe UI Emoji", 12),
                           fg_color="transparent", hover_color=Colors.ACCENT_RED_HOVER,
                           text_color=Colors.TEXT_MUTED,
                           command=lambda n=p.name: self._delete_participant(n)).pack(side="right")

        # Data management
        data_card = ctk.CTkFrame(scroll, corner_radius=14, fg_color=Colors.BG_CARD,
                                  border_width=1, border_color=Colors.BORDER)
        data_card.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))
        data_inner = ctk.CTkFrame(data_card, fg_color="transparent")
        data_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(data_inner, text="💾 Gestión de Datos", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.MD))

        btns = ctk.CTkFrame(data_inner, fg_color="transparent")
        btns.pack(fill="x")

        ctk.CTkButton(btns, text="📤 Exportar a JSON", font=Fonts.BODY_SM, height=36,
                       corner_radius=8, fg_color=Colors.BG_TERTIARY,
                       hover_color=Colors.BG_HOVER, border_width=1, border_color=Colors.BORDER,
                       text_color=Colors.TEXT_SECONDARY, command=self._export_json).pack(side="left", padx=(0, Spacing.SM))
        ctk.CTkButton(btns, text="📥 Exportar CSV", font=Fonts.BODY_SM, height=36,
                       corner_radius=8, fg_color=Colors.BG_TERTIARY,
                       hover_color=Colors.BG_HOVER, border_width=1, border_color=Colors.BORDER,
                       text_color=Colors.TEXT_SECONDARY, command=self._export_csv).pack(side="left")

        # Keyboard shortcuts
        shortcuts_card = ctk.CTkFrame(scroll, corner_radius=14, fg_color=Colors.BG_CARD,
                                       border_width=1, border_color=Colors.BORDER)
        shortcuts_card.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))
        sc_inner = ctk.CTkFrame(shortcuts_card, fg_color="transparent")
        sc_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(sc_inner, text="⌨️ Atajos de Teclado", font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(anchor="w", pady=(0, Spacing.MD))

        shortcuts = [
            ("Ctrl+N", "Crear liga nueva"),
            ("Ctrl+O", "Abrir liga"),
            ("Ctrl+S", "Guardar liga"),
            ("Ctrl+1-8", "Navegar entre secciones"),
        ]
        for key, action in shortcuts:
            row = ctk.CTkFrame(sc_inner, fg_color="transparent")
            row.pack(fill="x", pady=1)
            key_badge = ctk.CTkFrame(row, fg_color=Colors.BG_TERTIARY, corner_radius=6)
            key_badge.pack(side="left")
            ctk.CTkLabel(key_badge, text=key, font=Fonts.MONO_SM,
                          text_color=Colors.ACCENT_BLUE).pack(padx=Spacing.SM, pady=2)
            ctk.CTkLabel(row, text=action, font=Fonts.BODY_SM,
                          text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(Spacing.SM, 0))

    def _add_info_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=1)
        ctk.CTkLabel(row, text=label, font=Fonts.BODY_SM,
                      text_color=Colors.TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(row, text=value, font=Fonts.BODY_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(side="right")

    def _add_participant(self):
        dialog = ctk.CTkInputDialog(text="Nombre del nuevo participante:", title="Añadir Participante")
        name = dialog.get_input()
        if name and name.strip():
            colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
                      "#06b6d4", "#ec4899", "#14b8a6", "#f97316", "#6366f1"]
            count = len(self.db.get_participants())
            p = Participant(name=name.strip(), avatar_color=colors[count % len(colors)])
            self.db.add_participant(p)
            if self.on_refresh:
                self.on_refresh()

    def _delete_participant(self, name):
        from tkinter import messagebox
        if messagebox.askyesno("Confirmar", f"¿Eliminar a {name} y todo su historial?"):
            self.db.delete_participant(name)
            if self.on_refresh:
                self.on_refresh()

    def _export_json(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".json",
                                              filetypes=[("JSON", "*.json")])
        if path:
            self.db.export_to_json(path)
            from tkinter import messagebox
            messagebox.showinfo("Exportado", f"Liga exportada a:\n{path}")

    def _export_csv(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                              filetypes=[("CSV", "*.csv")])
        if path:
            self.db.export_transactions_csv(path)
            from tkinter import messagebox
            messagebox.showinfo("Exportado", f"Historial exportado a:\n{path}")

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
