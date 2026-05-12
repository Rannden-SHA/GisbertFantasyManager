"""
Players database view.
"""
import customtkinter as ctk
from config import Colors, Fonts, Spacing
from widgets.search_bar import SearchBar
from widgets.data_table import DataTable
from utils import format_money
from models import Player
from datetime import datetime


class PlayersView(ctk.CTkFrame):
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
        ctk.CTkLabel(header, text="👤 Base de Datos de Jugadores", font=Fonts.TITLE_LG,
                      text_color=Colors.TEXT_PRIMARY).pack(side="left")

        ctk.CTkButton(header, text="+ Añadir Jugador", font=Fonts.BODY_SM, height=36,
                       corner_radius=8, fg_color=Colors.ACCENT_BLUE,
                       hover_color=Colors.ACCENT_BLUE_HOVER,
                       command=self._add_player_dialog).pack(side="right")

        # Search
        self.search = SearchBar(scroll, placeholder="Buscar jugador...",
                                 on_search=self._on_search,
                                 filters=[{"id": "active", "label": "Activos"},
                                          {"id": "sold", "label": "Vendidos"},
                                          {"id": "free", "label": "Libres"}])
        self.search.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.MD))

        # Players table
        self._build_table(scroll)

    def _build_table(self, parent, search_term="", filter_id=None):
        if hasattr(self, 'table_frame'):
            self.table_frame.destroy()

        self.table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))

        players = self.db.get_players(status=filter_id or "")
        if search_term:
            players = [p for p in players if search_term.lower() in p.name.lower()
                       or search_term.lower() in p.team.lower()
                       or search_term.lower() in p.owner.lower()]

        columns = [
            {"key": "name", "label": "Jugador", "weight": 2},
            {"key": "team", "label": "Equipo", "weight": 1},
            {"key": "position", "label": "Pos", "weight": 1},
            {"key": "market_value", "label": "Valor Mercado", "weight": 1, "align": "e"},
            {"key": "owner", "label": "Propietario", "weight": 1},
            {"key": "purchase_price", "label": "Precio Compra", "weight": 1, "align": "e"},
            {"key": "status", "label": "Estado", "weight": 1},
        ]

        data = []
        for p in players:
            status_colors = {"active": Colors.ACCENT_GREEN, "sold": Colors.ACCENT_ORANGE, "free": Colors.TEXT_MUTED}
            data.append({
                "name": p.name,
                "team": p.team or "—",
                "position": p.position or "—",
                "market_value": format_money(p.market_value, True),
                "owner": p.owner or "Libre",
                "purchase_price": format_money(p.purchase_price, True) if p.purchase_price else "—",
                "status": p.status.capitalize(),
                "status_color": status_colors.get(p.status, Colors.TEXT_MUTED),
            })

        DataTable(self.table_frame, columns=columns, data=data,
                   title=f"{len(data)} jugadores").pack(fill="both", expand=True)

    def _on_search(self, term, filter_id):
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _add_player_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Añadir Jugador")
        dialog.geometry("400x500")
        dialog.configure(fg_color=Colors.BG_PRIMARY)
        dialog.transient(self)
        dialog.grab_set()

        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)

        ctk.CTkLabel(container, text="Añadir Jugador", font=Fonts.TITLE_MD,
                      text_color=Colors.TEXT_PRIMARY).pack(pady=(0, Spacing.LG))

        fields = {}
        for key, label in [("name", "Nombre"), ("team", "Equipo"),
                           ("position", "Posición (POR/DEF/MED/DEL)"),
                           ("market_value", "Valor de Mercado (€)")]:
            ctk.CTkLabel(container, text=label, font=Fonts.BODY_XS,
                          text_color=Colors.TEXT_SECONDARY).pack(anchor="w")
            entry = ctk.CTkEntry(container, font=Fonts.BODY, height=36, corner_radius=8,
                                  fg_color=Colors.BG_TERTIARY, border_color=Colors.BORDER,
                                  text_color=Colors.TEXT_PRIMARY, border_width=1)
            entry.pack(fill="x", pady=(2, Spacing.SM))
            fields[key] = entry

        # Owner dropdown
        participants = [p.name for p in self.db.get_participants()]
        ctk.CTkLabel(container, text="Propietario (opcional)", font=Fonts.BODY_XS,
                      text_color=Colors.TEXT_SECONDARY).pack(anchor="w")
        owner_dd = ctk.CTkComboBox(container, values=["Libre"] + participants,
                                    font=Fonts.BODY, height=36, corner_radius=8,
                                    fg_color=Colors.BG_TERTIARY, border_color=Colors.BORDER,
                                    text_color=Colors.TEXT_PRIMARY, border_width=1,
                                    button_color=Colors.ACCENT_BLUE,
                                    dropdown_fg_color=Colors.BG_TERTIARY,
                                    dropdown_text_color=Colors.TEXT_PRIMARY)
        owner_dd.pack(fill="x", pady=(2, Spacing.MD))
        owner_dd.set("Libre")

        def save():
            name = fields["name"].get().strip()
            if not name:
                return
            try:
                mv = float(fields["market_value"].get() or 0)
            except ValueError:
                mv = 0
            owner = owner_dd.get()
            if owner == "Libre":
                owner = ""
            player = Player(name=name, team=fields["team"].get().strip(),
                             position=fields["position"].get().strip().upper(),
                             market_value=mv, owner=owner,
                             purchase_date=datetime.now().isoformat(),
                             status="active" if owner else "free")
            self.db.add_player(player)
            dialog.destroy()
            self.refresh()

        ctk.CTkButton(container, text="✓ Guardar", font=Fonts.BODY, height=40,
                       corner_radius=10, fg_color=Colors.ACCENT_BLUE,
                       hover_color=Colors.ACCENT_BLUE_HOVER, command=save).pack(fill="x")

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
