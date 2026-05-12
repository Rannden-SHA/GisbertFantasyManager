"""
Welcome/landing view shown when no league is loaded.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing


class WelcomeView(ctk.CTkFrame):
    def __init__(self, parent, on_create, on_load, on_import, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.on_create = on_create
        self.on_load = on_load
        self.on_import = on_import
        self._build()

    def _build(self):
        # Center container
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.45, anchor="center")

        # Icon
        ctk.CTkLabel(center, text="⚽", font=("Segoe UI Emoji", 72)).pack(pady=(0, Spacing.LG))

        # Title
        ctk.CTkLabel(center, text="Gisbert's Fantasy Manager",
                      font=Fonts.TITLE_XL, text_color=Colors.TEXT_PRIMARY).pack()
        ctk.CTkLabel(center, text="Tu herramienta definitiva para La Liga Fantasy",
                      font=Fonts.BODY_LG, text_color=Colors.TEXT_SECONDARY).pack(pady=(Spacing.SM, Spacing.XXL))

        # Action buttons
        btn_frame = ctk.CTkFrame(center, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(btn_frame, text="🆕  Crear Liga Nueva", font=Fonts.BODY, width=220, height=48,
                       corner_radius=12, fg_color=Colors.ACCENT_BLUE,
                       hover_color=Colors.ACCENT_BLUE_HOVER, command=self.on_create).pack(pady=Spacing.SM)

        ctk.CTkButton(btn_frame, text="📂  Abrir Liga Existente", font=Fonts.BODY, width=220, height=48,
                       corner_radius=12, fg_color=Colors.BG_TERTIARY,
                       hover_color=Colors.BG_HOVER, border_width=1, border_color=Colors.BORDER,
                       command=self.on_load).pack(pady=Spacing.SM)

        ctk.CTkButton(btn_frame, text="📥  Importar Liga JSON (v1)", font=Fonts.BODY_SM, width=220, height=40,
                       corner_radius=10, fg_color="transparent",
                       hover_color=Colors.BG_HOVER, text_color=Colors.TEXT_MUTED,
                       command=self.on_import).pack(pady=Spacing.SM)

        # Footer
        ctk.CTkLabel(center, text="v2.0 • Compatible con archivos de la versión anterior",
                      font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED).pack(pady=(Spacing.XXL, 0))
