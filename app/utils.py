"""
Utility functions for Gisbert's Fantasy Manager v2.0
"""
from config import Fantasy, Colors


def format_money(amount: float, short: bool = False) -> str:
    """Format a number as money with European formatting.
    
    Args:
        amount: The amount to format
        short: If True, use abbreviated format (e.g., 1.5M, 250K)
    """
    if short:
        abs_amount = abs(amount)
        sign = "-" if amount < 0 else ""
        if abs_amount >= 1_000_000_000:
            return f"{sign}{abs_amount / 1_000_000_000:.1f}B€"
        elif abs_amount >= 1_000_000:
            return f"{sign}{abs_amount / 1_000_000:.1f}M€"
        elif abs_amount >= 1_000:
            return f"{sign}{abs_amount / 1_000:.0f}K€"
        else:
            return f"{sign}{abs_amount:.0f}€"
    else:
        return "{:,.0f}€".format(amount).replace(",", ".")


def format_number(number: float) -> str:
    """Format number with European thousands separator."""
    return "{:,.0f}".format(int(number)).replace(",", ".")


def format_percent(value: float) -> str:
    """Format as percentage."""
    return f"{value:+.1f}%"


def calculate_max_bid(saldo: float, valor_equipo: float) -> float:
    """Calculate maximum bid amount."""
    return saldo + Fantasy.MAX_BID_TEAM_PERCENT * valor_equipo


def calculate_clausula(market_value: float) -> float:
    """Calculate clausula price for a player.
    
    Rules:
    - If market_value < 1M → clausula = 1M
    - If market_value >= 1M → clausula = 66% of market value
    """
    if market_value < Fantasy.CLAUSULA_THRESHOLD:
        return Fantasy.CLAUSULA_BELOW_THRESHOLD
    return market_value * Fantasy.CLAUSULA_PERCENT


def calculate_overbid_percent(purchase_price: float, market_value: float) -> float:
    """Calculate overbid percentage."""
    if market_value <= 0:
        return 0.0
    return (purchase_price / market_value * 100) - 100


def get_saldo_color(saldo: float) -> str:
    """Get color based on saldo value."""
    if saldo < 0:
        return Colors.ACCENT_RED
    elif saldo > 0:
        return Colors.ACCENT_GREEN
    return Colors.TEXT_SECONDARY


def get_rank_color(rank: int) -> str:
    """Get color for ranking position."""
    if rank == 1:
        return Colors.GOLD
    elif rank == 2:
        return Colors.SILVER
    elif rank == 3:
        return Colors.BRONZE
    return Colors.TEXT_SECONDARY


def get_rank_medal(rank: int) -> str:
    """Get medal emoji for ranking position."""
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    return medals.get(rank, f"#{rank}")


def get_budget_health(saldo: float, initial_budget: float) -> tuple:
    """Get budget health status as (label, color, percentage).
    
    Returns:
        Tuple of (label, color, percentage 0-1)
    """
    if initial_budget <= 0:
        return ("N/A", Colors.TEXT_MUTED, 0)
    
    ratio = saldo / initial_budget
    if ratio > 0.5:
        return ("Excelente", Colors.ACCENT_GREEN, min(ratio, 1.0))
    elif ratio > 0.2:
        return ("Bueno", Colors.ACCENT_BLUE, ratio)
    elif ratio > 0:
        return ("Bajo", Colors.ACCENT_ORANGE, ratio)
    else:
        return ("¡Peligro!", Colors.ACCENT_RED, max(ratio, 0))


def points_to_money(points: int) -> float:
    """Convert fantasy points to money."""
    return points * Fantasy.POINTS_TO_MONEY_MULTIPLIER


def get_transaction_icon(tx_type: str) -> str:
    """Get icon for transaction type."""
    return Fantasy.TRANSACTION_TYPES.get(tx_type, {}).get("icon", "📝")


def get_transaction_label(tx_type: str) -> str:
    """Get label for transaction type."""
    return Fantasy.TRANSACTION_TYPES.get(tx_type, {}).get("label", tx_type)


def get_transaction_color(tx_type: str) -> str:
    """Get color for transaction type."""
    return Fantasy.TRANSACTION_TYPES.get(tx_type, {}).get("color", Colors.TEXT_SECONDARY)
