from pony.orm import select
from models import Obstacle, Game


def is_blocked_by_obstacle(game: Game, player_position: int, next_player_position: int):
    """
    Obstacles are always at the right side of players
    This means that if obstacle.position == player.position there's an
    obstacle to the right side of the player.

    Therefore we have two cases:
        - Game goes to the right: we check for obstacles at the right side
        of current player (player_position == obstacle_position)
        - Game goes to the left: we check for obstacles at the right side of
        next player (left side of current_player)
    """
    relevant_position = player_position if game.game_order == "right" else next_player_position
    # game direction right
    is_blocked = select(
        obs for obs in Obstacle if relevant_position == obs.position
    ).exists()
    return is_blocked
