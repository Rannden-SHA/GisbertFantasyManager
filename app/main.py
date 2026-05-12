"""
Gisbert's Fantasy Manager v2.0
Main application entry point.
A modern desktop app for managing La Liga Fantasy leagues.
"""
import customtkinter as ctk
import os
import sys
from tkinter import filedialog, messagebox

from config import (
    APP_NAME, APP_VERSION, Colors, Fonts, Spacing,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, SIDEBAR_WIDTH, NAV_ITEMS
)
from database import Database
from models import LeagueConfig, Participant
from widgets.sidebar import Sidebar
from views.welcome_view import WelcomeView
from views.dashboard_view import DashboardView
from views.market_view import MarketView
from views.players_view import PlayersView
from views.analytics_view import AnalyticsView
from views.history_view import HistoryView
from views.jornada_view import JornadaView
from views.clausulazo_view import ClausulazoView
from views.settings_view import SettingsView


class FantasyManagerApp(ctk.CTk):
    """Main application class for Gisbert's Fantasy Manager v2.0."""

    def __init__(self):
        super().__init__()

        # ─── Window setup ─────────────────────────────────────────
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.configure(fg_color=Colors.BG_PRIMARY)

        # Set icon
        icon_path = self._get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # ─── Theme ────────────────────────────────────────────────
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ─── State ────────────────────────────────────────────────
        self.db = Database()
        self.league_loaded = False
        self.current_view = None
        self.sidebar = None

        # ─── Build UI ─────────────────────────────────────────────
        self._build_layout()
        self._show_welcome()

        # ─── Keyboard shortcuts ───────────────────────────────────
        self._bind_shortcuts()

        # ─── Window close ─────────────────────────────────────────
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_resource_path(self, filename):
        """Get absolute path to a resource file."""
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, filename)

    def _build_layout(self):
        """Build the main layout structure."""
        # Top bar
        self.topbar = ctk.CTkFrame(self, height=50, fg_color=Colors.BG_SECONDARY, corner_radius=0)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)
        self._build_topbar()

        # Body: sidebar + content
        self.body = ctk.CTkFrame(self, fg_color=Colors.BG_PRIMARY, corner_radius=0)
        self.body.pack(fill="both", expand=True)

        # Content area (sidebar added when league loaded)
        self.content_frame = ctk.CTkFrame(self.body, fg_color=Colors.BG_PRIMARY, corner_radius=0)
        self.content_frame.pack(fill="both", expand=True)

        # Status bar
        self.statusbar = ctk.CTkFrame(self, height=28, fg_color=Colors.BG_SECONDARY, corner_radius=0)
        self.statusbar.pack(fill="x")
        self.statusbar.pack_propagate(False)
        self._build_statusbar()

    def _build_topbar(self):
        """Build the top navigation bar."""
        inner = ctk.CTkFrame(self.topbar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=Spacing.MD)

        # Left: App name
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        ctk.CTkLabel(left, text="⚽", font=("Segoe UI Emoji", 20)).pack(side="left", padx=(0, Spacing.SM))
        ctk.CTkLabel(left, text=APP_NAME, font=Fonts.TITLE_SM,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left")

        # Center: league name
        self.league_label = ctk.CTkLabel(inner, text="", font=Fonts.BODY,
                                          text_color=Colors.TEXT_SECONDARY)
        self.league_label.pack(side="left", padx=Spacing.XL)

        # Right: Quick actions
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", fill="y")

        ctk.CTkButton(right, text="📂", width=36, height=36, font=("Segoe UI Emoji", 16),
                       corner_radius=8, fg_color="transparent", hover_color=Colors.BG_HOVER,
                       command=self._load_league).pack(side="left", padx=2)
        ctk.CTkButton(right, text="🆕", width=36, height=36, font=("Segoe UI Emoji", 16),
                       corner_radius=8, fg_color="transparent", hover_color=Colors.BG_HOVER,
                       command=self._create_league).pack(side="left", padx=2)

    def _build_statusbar(self):
        """Build the bottom status bar."""
        inner = ctk.CTkFrame(self.statusbar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=Spacing.MD)

        self.status_text = ctk.CTkLabel(inner, text="Listo", font=Fonts.CAPTION,
                                         text_color=Colors.TEXT_MUTED)
        self.status_text.pack(side="left")

        ctk.CTkLabel(inner, text=f"v{APP_VERSION}", font=Fonts.CAPTION,
                      text_color=Colors.TEXT_DISABLED).pack(side="right")

    def _bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.bind("<Control-n>", lambda e: self._create_league())
        self.bind("<Control-N>", lambda e: self._create_league())
        self.bind("<Control-o>", lambda e: self._load_league())
        self.bind("<Control-O>", lambda e: self._load_league())
        self.bind("<Control-s>", lambda e: self._save_league())
        self.bind("<Control-S>", lambda e: self._save_league())

        # Navigate with Ctrl+number
        for i, item in enumerate(NAV_ITEMS):
            key = str(i + 1)
            self.bind(f"<Control-Key-{key}>",
                      lambda e, nav_id=item["id"]: self._navigate(nav_id))

    # ─── Navigation ──────────────────────────────────────────────

    def _show_welcome(self):
        """Show the welcome/landing view."""
        self._clear_content()
        if self.sidebar:
            self.sidebar.pack_forget()
        welcome = WelcomeView(self.content_frame,
                               on_create=self._create_league,
                               on_load=self._load_league,
                               on_import=self._import_json)
        welcome.pack(fill="both", expand=True)
        self.current_view = welcome

    def _show_main(self):
        """Switch to the main app layout with sidebar."""
        self._clear_content()

        # Add sidebar
        if self.sidebar:
            self.sidebar.destroy()

        self.sidebar = Sidebar(self.body, on_navigate=self._navigate)
        self.body.pack_propagate(False)

        # Re-pack: sidebar left, content right
        self.content_frame.pack_forget()
        self.sidebar.pack(side="left", fill="y")
        self.content_frame.pack(side="left", fill="both", expand=True)

        self._navigate("dashboard")

    def _navigate(self, view_id: str):
        """Navigate to a specific view."""
        if not self.league_loaded:
            return

        self._clear_content()

        if self.sidebar:
            self.sidebar._set_active(view_id)

        view_map = {
            "dashboard": lambda: DashboardView(self.content_frame, self.db, on_navigate=self._navigate),
            "market": lambda: MarketView(self.content_frame, self.db, on_refresh=self._refresh_current),
            "players": lambda: PlayersView(self.content_frame, self.db),
            "analytics": lambda: AnalyticsView(self.content_frame, self.db),
            "history": lambda: HistoryView(self.content_frame, self.db),
            "jornada": lambda: JornadaView(self.content_frame, self.db, on_refresh=self._refresh_current),
            "clausulazo": lambda: ClausulazoView(self.content_frame, self.db),
            "settings": lambda: SettingsView(self.content_frame, self.db, on_refresh=self._refresh_current),
        }

        factory = view_map.get(view_id)
        if factory:
            self.current_view = factory()
            self.current_view.pack(fill="both", expand=True)
            self._current_view_id = view_id
            self._update_status(f"Vista: {view_id.capitalize()}")

    def _clear_content(self):
        """Clear the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_view = None

    def _refresh_current(self):
        """Refresh the current view."""
        if hasattr(self, '_current_view_id'):
            self._navigate(self._current_view_id)

    # ─── League Management ───────────────────────────────────────

    def _create_league(self):
        """Create a new league via dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Crear Nueva Liga")
        dialog.geometry("500x450")
        dialog.configure(fg_color=Colors.BG_PRIMARY)
        dialog.transient(self)
        dialog.grab_set()

        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.XL)

        ctk.CTkLabel(container, text="🆕 Crear Nueva Liga", font=Fonts.TITLE_LG,
                      text_color=Colors.TEXT_PRIMARY).pack(pady=(0, Spacing.LG))

        # League name
        ctk.CTkLabel(container, text="Nombre de la Liga", font=Fonts.BODY_SM,
                      text_color=Colors.TEXT_SECONDARY).pack(anchor="w")
        name_entry = ctk.CTkEntry(container, placeholder_text="Ej: Liga Gisbert 2025",
                                    font=Fonts.BODY, height=40, corner_radius=10,
                                    fg_color=Colors.BG_TERTIARY, border_color=Colors.BORDER,
                                    text_color=Colors.TEXT_PRIMARY, border_width=1)
        name_entry.pack(fill="x", pady=(4, Spacing.MD))

        # Participants
        ctk.CTkLabel(container, text="Participantes (separados por comas)", font=Fonts.BODY_SM,
                      text_color=Colors.TEXT_SECONDARY).pack(anchor="w")
        part_entry = ctk.CTkEntry(container, placeholder_text="Ej: Carlos, Ana, Pedro, María",
                                    font=Fonts.BODY, height=40, corner_radius=10,
                                    fg_color=Colors.BG_TERTIARY, border_color=Colors.BORDER,
                                    text_color=Colors.TEXT_PRIMARY, border_width=1)
        part_entry.pack(fill="x", pady=(4, Spacing.MD))

        # Initial budget
        ctk.CTkLabel(container, text="Presupuesto Inicial (€)", font=Fonts.BODY_SM,
                      text_color=Colors.TEXT_SECONDARY).pack(anchor="w")
        budget_entry = ctk.CTkEntry(container, placeholder_text="100000000",
                                      font=Fonts.BODY, height=40, corner_radius=10,
                                      fg_color=Colors.BG_TERTIARY, border_color=Colors.BORDER,
                                      text_color=Colors.TEXT_PRIMARY, border_width=1)
        budget_entry.pack(fill="x", pady=(4, Spacing.MD))
        budget_entry.insert(0, "100000000")

        def create():
            league_name = name_entry.get().strip()
            participants_str = part_entry.get().strip()
            if not league_name or not participants_str:
                messagebox.showwarning("Error", "Introduce nombre de liga y participantes")
                return

            try:
                budget = float(budget_entry.get().replace(".", "").replace(",", ""))
            except ValueError:
                budget = 100_000_000

            participant_names = [n.strip() for n in participants_str.split(",") if n.strip()]
            if not participant_names:
                messagebox.showwarning("Error", "Introduce al menos un participante")
                return

            # Create database
            data_dir = self._get_resource_path("data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, f"{league_name}.db")

            self.db.connect(db_path)

            # Save config
            config = LeagueConfig(name=league_name, initial_budget=budget)
            self.db.save_config(config)

            # Add participants
            avatar_colors = [
                "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
                "#06b6d4", "#ec4899", "#14b8a6", "#f97316", "#6366f1"
            ]
            for i, name in enumerate(participant_names):
                p = Participant(name=name, saldo=0, avatar_color=avatar_colors[i % len(avatar_colors)])
                self.db.add_participant(p)

            self.league_loaded = True
            self._update_league_label(league_name)
            dialog.destroy()
            self._show_main()
            self._update_status(f"Liga '{league_name}' creada con {len(participant_names)} participantes")

        ctk.CTkButton(container, text="✓ Crear Liga", font=Fonts.BODY, height=44,
                       corner_radius=12, fg_color=Colors.ACCENT_BLUE,
                       hover_color=Colors.ACCENT_BLUE_HOVER, command=create).pack(fill="x", pady=(Spacing.MD, 0))

    def _load_league(self):
        """Load an existing league database."""
        data_dir = self._get_resource_path("data")
        os.makedirs(data_dir, exist_ok=True)

        file_path = filedialog.askopenfilename(
            title="Abrir Liga",
            initialdir=data_dir,
            filetypes=[("League Database", "*.db"), ("JSON (v1)", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return

        if file_path.endswith(".json"):
            # Import old format
            self._import_json_file(file_path)
        else:
            self.db.connect(file_path)
            config = self.db.get_config()
            if not config:
                messagebox.showerror("Error", "No se encontró configuración de liga en este archivo")
                return

            self.league_loaded = True
            self._update_league_label(config.name)
            self._show_main()
            self._update_status(f"Liga '{config.name}' cargada")

    def _import_json(self):
        """Import from old JSON format (v1 compatibility)."""
        file_path = filedialog.askopenfilename(
            title="Importar Liga JSON (v1)",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            self._import_json_file(file_path)

    def _import_json_file(self, json_path: str):
        """Import a specific JSON file."""
        league_name = os.path.basename(json_path).replace(".json", "")
        data_dir = self._get_resource_path("data")
        os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, f"{league_name}.db")

        self.db.connect(db_path)
        try:
            self.db.import_from_json(json_path, league_name)
            self.league_loaded = True
            self._update_league_label(league_name)
            self._show_main()
            self._update_status(f"Liga '{league_name}' importada desde JSON v1")
            messagebox.showinfo("Importación Exitosa",
                                f"Liga '{league_name}' importada correctamente.\n"
                                f"Los datos se han convertido al nuevo formato.")
        except Exception as e:
            messagebox.showerror("Error de Importación", f"No se pudo importar: {str(e)}")

    def _save_league(self):
        """Manual save (auto-save is default)."""
        if self.league_loaded and self.db.conn:
            self.db.conn.commit()
            self._update_status("Liga guardada ✓")

    # ─── UI Helpers ──────────────────────────────────────────────

    def _update_league_label(self, name: str):
        """Update the league name in the top bar."""
        self.league_label.configure(text=f"Liga: {name}")
        self.title(f"{APP_NAME} — {name}")

    def _update_status(self, text: str):
        """Update status bar text."""
        self.status_text.configure(text=text)

    def _on_close(self):
        """Handle window close."""
        if self.league_loaded:
            self._save_league()
        self.db.close()
        self.destroy()


def main():
    app = FantasyManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
