from models import Game
from lacosa.room.utils.room_operations import delete_room
import asyncio


def _is_the_thing_dead(game: Game):
    is_thing_alive = game.players.filter(
        lambda player: player.role == "thing"
    ).first().is_alive

    return not is_thing_alive


def _is_only_one_human_alive(game: Game):
    human_count = game.players.filter(
        lambda player: player.role == "human" and player.is_alive
    ).count()

    return human_count == 1


def _is_only_one_player_alive(game: Game):
    alive_players = game.players.filter(
        lambda player: player.is_alive
    )

    return alive_players.count() == 1, alive_players.first()


def _get_winner(game: Game):
    """
    returns role of winner faction.
    Possible returns are: 'human', 'thing'
    """
    is_one_player_left, player_left = _is_only_one_player_alive(game)
    is_thing_is_dead = _is_the_thing_dead(game)
    is_one_human_left = _is_only_one_human_alive(game)

    if is_thing_is_dead:
        return "human"
    elif is_one_player_left:
        return player_left.role
    elif is_one_human_left:
        return "thing"
    else:
        return None


def _update_game_state(game: Game, winner: str):
    if winner == "human":
        game.have_humans_won = True
    elif winner == "thing":
        game.have_humans_won = False

    game.is_game_over = True


async def end_game_if_conditions_are_met(game: Game, time_before_close=30) -> None:
    winner = _get_winner(game)

    if winner is not None:
        _update_game_state(game, winner)
        await asyncio.sleep(time_before_close)
        delete_room(game.waiting_room)
