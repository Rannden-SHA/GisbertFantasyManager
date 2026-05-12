"""
SQLite database layer for Gisbert's Fantasy Manager v2.0
Handles all data persistence with backward compatibility for old JSON format.
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional
from models import Transaction, Participant, JornadaRecord, Player, LeagueConfig


class Database:
    """SQLite database manager for the Fantasy League."""

    def __init__(self, db_path: str = ""):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        if db_path:
            self.connect(db_path)

    def connect(self, db_path: str):
        """Connect to database and ensure tables exist."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS league_config (
                id INTEGER PRIMARY KEY DEFAULT 1,
                name TEXT NOT NULL,
                created_at TEXT,
                initial_budget REAL DEFAULT 100000000,
                points_multiplier REAL DEFAULT 100000,
                max_bid_percent REAL DEFAULT 0.20,
                current_jornada INTEGER DEFAULT 0,
                auto_save INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS participants (
                name TEXT PRIMARY KEY,
                saldo REAL DEFAULT 0,
                valor_equipo REAL DEFAULT 0,
                total_points INTEGER DEFAULT 0,
                avatar_color TEXT DEFAULT '#3b82f6'
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant TEXT NOT NULL,
                type TEXT NOT NULL,
                player_name TEXT DEFAULT '',
                amount REAL DEFAULT 0,
                market_value REAL DEFAULT 0,
                saldo_before REAL DEFAULT 0,
                saldo_after REAL DEFAULT 0,
                overbid_percent REAL DEFAULT 0,
                timestamp TEXT,
                jornada INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                FOREIGN KEY (participant) REFERENCES participants(name)
            );

            CREATE TABLE IF NOT EXISTS jornadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant TEXT NOT NULL,
                jornada INTEGER NOT NULL,
                points INTEGER DEFAULT 0,
                money_earned REAL DEFAULT 0,
                timestamp TEXT,
                FOREIGN KEY (participant) REFERENCES participants(name),
                UNIQUE(participant, jornada)
            );

            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                team TEXT DEFAULT '',
                position TEXT DEFAULT '',
                market_value REAL DEFAULT 0,
                owner TEXT DEFAULT '',
                purchase_price REAL DEFAULT 0,
                purchase_date TEXT DEFAULT '',
                status TEXT DEFAULT 'active'
            );
        """)
        self.conn.commit()

    # ─── League Config ──────────────────────────────────────────────

    def save_config(self, config: LeagueConfig):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO league_config 
            (id, name, created_at, initial_budget, points_multiplier, max_bid_percent, current_jornada, auto_save)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        """, (config.name, config.created_at, config.initial_budget,
              config.points_multiplier, config.max_bid_percent,
              config.current_jornada, 1 if config.auto_save else 0))
        self.conn.commit()

    def get_config(self) -> Optional[LeagueConfig]:
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM league_config WHERE id = 1").fetchone()
        if not row:
            return None
        return LeagueConfig(
            name=row["name"],
            created_at=row["created_at"],
            initial_budget=row["initial_budget"],
            points_multiplier=row["points_multiplier"],
            max_bid_percent=row["max_bid_percent"],
            current_jornada=row["current_jornada"],
            auto_save=bool(row["auto_save"])
        )

    # ─── Participants ───────────────────────────────────────────────

    def add_participant(self, participant: Participant):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO participants (name, saldo, valor_equipo, total_points, avatar_color)
            VALUES (?, ?, ?, ?, ?)
        """, (participant.name, participant.saldo, participant.valor_equipo,
              participant.total_points, participant.avatar_color))
        self.conn.commit()

    def get_participants(self) -> list:
        cursor = self.conn.cursor()
        rows = cursor.execute("SELECT * FROM participants ORDER BY name").fetchall()
        return [Participant(
            name=r["name"], saldo=r["saldo"], valor_equipo=r["valor_equipo"],
            total_points=r["total_points"], avatar_color=r["avatar_color"]
        ) for r in rows]

    def get_participant(self, name: str) -> Optional[Participant]:
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT * FROM participants WHERE name = ?", (name,)).fetchone()
        if not row:
            return None
        return Participant(
            name=row["name"], saldo=row["saldo"], valor_equipo=row["valor_equipo"],
            total_points=row["total_points"], avatar_color=row["avatar_color"]
        )

    def update_participant_saldo(self, name: str, new_saldo: float):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE participants SET saldo = ? WHERE name = ?", (new_saldo, name))
        self.conn.commit()

    def update_participant_team_value(self, name: str, new_value: float):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE participants SET valor_equipo = ? WHERE name = ?", (new_value, name))
        self.conn.commit()

    def update_participant_points(self, name: str, total_points: int):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE participants SET total_points = ? WHERE name = ?", (total_points, name))
        self.conn.commit()

    def delete_participant(self, name: str):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM participants WHERE name = ?", (name,))
        cursor.execute("DELETE FROM transactions WHERE participant = ?", (name,))
        cursor.execute("DELETE FROM jornadas WHERE participant = ?", (name,))
        self.conn.commit()

    # ─── Transactions ───────────────────────────────────────────────

    def add_transaction(self, tx: Transaction) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO transactions 
            (participant, type, player_name, amount, market_value, saldo_before, saldo_after, 
             overbid_percent, timestamp, jornada, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tx.participant, tx.type, tx.player_name, tx.amount, tx.market_value,
              tx.saldo_before, tx.saldo_after, tx.overbid_percent, tx.timestamp,
              tx.jornada, tx.notes))
        self.conn.commit()
        return cursor.lastrowid

    def get_transactions(self, participant: str = "", tx_type: str = "", limit: int = 0) -> list:
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        if participant:
            query += " AND participant = ?"
            params.append(participant)
        if tx_type:
            query += " AND type = ?"
            params.append(tx_type)
        query += " ORDER BY id DESC"
        if limit > 0:
            query += f" LIMIT {limit}"

        cursor = self.conn.cursor()
        rows = cursor.execute(query, params).fetchall()
        return [Transaction(
            id=r["id"], participant=r["participant"], type=r["type"],
            player_name=r["player_name"], amount=r["amount"], market_value=r["market_value"],
            saldo_before=r["saldo_before"], saldo_after=r["saldo_after"],
            overbid_percent=r["overbid_percent"], timestamp=r["timestamp"],
            jornada=r["jornada"], notes=r["notes"]
        ) for r in rows]

    def get_last_transaction(self) -> Optional[Transaction]:
        txs = self.get_transactions(limit=1)
        return txs[0] if txs else None

    def delete_transaction(self, tx_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
        self.conn.commit()

    def get_purchase_overbids(self, participant: str) -> list:
        """Get list of overbid percentages for a participant's purchases."""
        cursor = self.conn.cursor()
        rows = cursor.execute(
            "SELECT overbid_percent FROM transactions WHERE participant = ? AND type = 'purchase'",
            (participant,)
        ).fetchall()
        return [r["overbid_percent"] for r in rows]

    # ─── Jornadas ───────────────────────────────────────────────────

    def add_jornada(self, record: JornadaRecord):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO jornadas (participant, jornada, points, money_earned, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (record.participant, record.jornada, record.points,
              record.money_earned, record.timestamp))
        self.conn.commit()

    def get_jornadas(self, participant: str = "") -> list:
        query = "SELECT * FROM jornadas"
        params = []
        if participant:
            query += " WHERE participant = ?"
            params.append(participant)
        query += " ORDER BY jornada ASC"

        cursor = self.conn.cursor()
        rows = cursor.execute(query, params).fetchall()
        return [JornadaRecord(
            id=r["id"], participant=r["participant"], jornada=r["jornada"],
            points=r["points"], money_earned=r["money_earned"], timestamp=r["timestamp"]
        ) for r in rows]

    def get_jornada_by_number(self, jornada: int) -> list:
        cursor = self.conn.cursor()
        rows = cursor.execute(
            "SELECT * FROM jornadas WHERE jornada = ? ORDER BY points DESC", (jornada,)
        ).fetchall()
        return [JornadaRecord(
            id=r["id"], participant=r["participant"], jornada=r["jornada"],
            points=r["points"], money_earned=r["money_earned"], timestamp=r["timestamp"]
        ) for r in rows]

    # ─── Players ────────────────────────────────────────────────────

    def add_player(self, player: Player) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO players (name, team, position, market_value, owner, purchase_price, purchase_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (player.name, player.team, player.position, player.market_value,
              player.owner, player.purchase_price, player.purchase_date, player.status))
        self.conn.commit()
        return cursor.lastrowid

    def get_players(self, owner: str = "", status: str = "") -> list:
        query = "SELECT * FROM players WHERE 1=1"
        params = []
        if owner:
            query += " AND owner = ?"
            params.append(owner)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY name"

        cursor = self.conn.cursor()
        rows = cursor.execute(query, params).fetchall()
        return [Player(
            id=r["id"], name=r["name"], team=r["team"], position=r["position"],
            market_value=r["market_value"], owner=r["owner"],
            purchase_price=r["purchase_price"], purchase_date=r["purchase_date"],
            status=r["status"]
        ) for r in rows]

    def update_player_owner(self, player_id: int, new_owner: str, purchase_price: float = 0):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE players SET owner = ?, purchase_price = ?, 
            purchase_date = ?, status = ?
            WHERE id = ?
        """, (new_owner, purchase_price, datetime.now().isoformat(),
              "active" if new_owner else "free", player_id))
        self.conn.commit()

    def update_player_value(self, player_id: int, new_value: float):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE players SET market_value = ? WHERE id = ?", (new_value, player_id))
        self.conn.commit()

    def delete_player(self, player_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
        self.conn.commit()

    # ─── Import from Old JSON Format ────────────────────────────────

    def import_from_json(self, json_path: str, league_name: str = ""):
        """Import data from old JSON format for backward compatibility."""
        with open(json_path, "r", encoding="utf-8") as f:
            old_data = json.load(f)

        if not league_name:
            league_name = os.path.basename(json_path).replace(".json", "")

        # Create config
        config = LeagueConfig(name=league_name)
        self.save_config(config)

        # Import participants
        avatar_colors = [
            "#3b82f6", "#10b981", "#f59e0b", "#ef4444",
            "#8b5cf6", "#06b6d4", "#ec4899", "#14b8a6",
            "#f97316", "#6366f1", "#84cc16", "#e879f9"
        ]

        for i, (name, data) in enumerate(old_data.items()):
            participant = Participant(
                name=name,
                saldo=data.get("saldo", 0),
                valor_equipo=data.get("valor_equipo", 0),
                total_points=0,
                avatar_color=avatar_colors[i % len(avatar_colors)]
            )
            self.add_participant(participant)

            # Import history as transactions
            for record in data.get("historial", []):
                tx = Transaction(
                    participant=name,
                    type=self._guess_transaction_type(record),
                    notes=record,
                    timestamp=datetime.now().isoformat()
                )
                # Try to parse amounts from the record string
                if "Precio:" in record:
                    try:
                        price_str = record.split("Precio:")[1].split("€")[0].strip()
                        price_str = price_str.replace(".", "").replace(",", ".")
                        tx.amount = float(price_str)
                    except (ValueError, IndexError):
                        pass
                self.add_transaction(tx)

        return True

    def _guess_transaction_type(self, record: str) -> str:
        """Guess transaction type from old format history string."""
        record_lower = record.lower()
        if "compra" in record_lower:
            return "purchase"
        elif "venta" in record_lower:
            return "sale"
        elif "punto" in record_lower:
            return "points"
        elif "dinero" in record_lower or "adición" in record_lower:
            return "money"
        elif "valor" in record_lower and "equipo" in record_lower:
            return "team_value"
        return "money"

    # ─── Export ──────────────────────────────────────────────────────

    def export_to_json(self, json_path: str):
        """Export current data to JSON format."""
        participants = self.get_participants()
        data = {}
        for p in participants:
            txs = self.get_transactions(participant=p.name)
            data[p.name] = {
                "saldo": p.saldo,
                "valor_equipo": p.valor_equipo,
                "total_points": p.total_points,
                "historial": [tx.notes or f"{tx.type}: {tx.player_name} - {tx.amount}€" for tx in reversed(txs)],
                "purchases": self.get_purchase_overbids(p.name)
            }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def export_transactions_csv(self, csv_path: str):
        """Export all transactions to CSV."""
        txs = self.get_transactions()
        import csv
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Participante", "Tipo", "Jugador", "Cantidad",
                           "Valor Mercado", "Saldo Antes", "Saldo Después",
                           "% Sobrepuja", "Fecha", "Jornada", "Notas"])
            for tx in txs:
                writer.writerow([tx.id, tx.participant, tx.type, tx.player_name,
                               tx.amount, tx.market_value, tx.saldo_before,
                               tx.saldo_after, tx.overbid_percent, tx.timestamp,
                               tx.jornada, tx.notes])

    # ─── Statistics ─────────────────────────────────────────────────

    def get_total_transactions_count(self) -> int:
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT COUNT(*) as cnt FROM transactions").fetchone()
        return row["cnt"]

    def get_total_money_moved(self) -> float:
        cursor = self.conn.cursor()
        row = cursor.execute("SELECT COALESCE(SUM(ABS(amount)), 0) as total FROM transactions").fetchone()
        return row["total"]

    def get_participant_stats(self, name: str) -> dict:
        """Get comprehensive stats for a participant."""
        cursor = self.conn.cursor()
        purchases = cursor.execute(
            "SELECT COUNT(*) as cnt, COALESCE(SUM(amount), 0) as total FROM transactions WHERE participant = ? AND type = 'purchase'",
            (name,)
        ).fetchone()
        sales = cursor.execute(
            "SELECT COUNT(*) as cnt, COALESCE(SUM(amount), 0) as total FROM transactions WHERE participant = ? AND type = 'sale'",
            (name,)
        ).fetchone()
        overbids = self.get_purchase_overbids(name)

        return {
            "total_purchases": purchases["cnt"],
            "total_spent": purchases["total"],
            "total_sales": sales["cnt"],
            "total_earned": sales["total"],
            "avg_overbid": sum(overbids) / len(overbids) if overbids else 0,
            "max_overbid": max(overbids) if overbids else 0,
            "min_overbid": min(overbids) if overbids else 0,
        }
