"""
Data models for Gisbert's Fantasy Manager v2.0
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Transaction:
    """Represents a single transaction in the league."""
    id: Optional[int] = None
    participant: str = ""
    type: str = ""  # purchase, sale, money, points, team_value
    player_name: str = ""
    amount: float = 0.0
    market_value: float = 0.0
    saldo_before: float = 0.0
    saldo_after: float = 0.0
    overbid_percent: float = 0.0
    timestamp: str = ""
    jornada: int = 0
    notes: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Participant:
    """Represents a league participant/manager."""
    name: str = ""
    saldo: float = 0.0
    valor_equipo: float = 0.0
    total_points: int = 0
    avatar_color: str = "#3b82f6"

    @property
    def valor_total(self) -> float:
        return self.saldo + self.valor_equipo

    @property
    def max_bid(self) -> float:
        return self.saldo + 0.20 * self.valor_equipo

    def overbid_avg(self, purchases: list) -> float:
        if not purchases:
            return 0.0
        return sum(purchases) / len(purchases)


@dataclass
class JornadaRecord:
    """Records points for a specific jornada."""
    id: Optional[int] = None
    participant: str = ""
    jornada: int = 0
    points: int = 0
    money_earned: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class Player:
    """Represents a football player tracked in the league."""
    id: Optional[int] = None
    name: str = ""
    team: str = ""
    position: str = ""
    market_value: float = 0.0
    owner: str = ""  # Participant who owns them, empty if free
    purchase_price: float = 0.0
    purchase_date: str = ""
    status: str = "active"  # active, sold, free


@dataclass
class LeagueConfig:
    """League configuration."""
    name: str = ""
    created_at: str = ""
    initial_budget: float = 100_000_000
    points_multiplier: float = 100_000
    max_bid_percent: float = 0.20
    current_jornada: int = 0
    auto_save: bool = True

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
