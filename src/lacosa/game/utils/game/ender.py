from models import Game
from pony.orm import db_session, commit
from lacosa.utils import find_game


def _is_the_thing_dead(game: Game):
    thing = game.players.filter(lambda player: player.role == "thing").first()

    if thing is None:
        return True

    return not thing.is_alive


def _are_all_humans_dead(game: Game):
    human_count = game.players.filter(
        lambda player: player.role == "human" and player.is_alive
    ).count()

    return human_count == 0


def _is_only_one_player_alive(game: Game):
    alive_players = game.players.filter(lambda player: player.is_alive)

    return alive_players.count() == 1, alive_players.first()


def _get_winner(game: Game):
    """
    returns role of winner faction.
    Possible returns are: 'human', 'thing'
    """
    is_one_player_left, player_left = _is_only_one_player_alive(game)
    is_thing_is_dead = _is_the_thing_dead(game)
    no_humans_left = _are_all_humans_dead(game)

    if is_thing_is_dead:
        return "human"
    elif is_one_player_left:
        return player_left.role
    elif no_humans_left:
        return "thing"
    else:
        return None


def _update_game_state(game: Game, winner: str):
    if winner == "human":
        game.have_humans_won = True
    elif winner == "thing":
        game.have_humans_won = False

    game.is_game_over = True


def end_game_if_conditions_are_met(game: Game, time_before_close=30) -> None:
    winner = _get_winner(game)

    if winner is not None:
        _update_game_state(game, winner)
        # await asyncio.sleep(time_before_close)
        # delete_room(game.waiting_room)


# eliminar jugador si la partida ya termino y borrarla si no hay mas jugadores
def leave_game_if_conditions_are_met(room_id: int, player_id: int) -> None:
    game = find_game(room_id)
    player = game.players.filter(lambda p: p.id == player_id).first()

    if game.is_game_over:
        player.delete()
        commit()
        if game.players.count() == 0:
            delete_room(game.waiting_room)


def delete_room(room):
    room.delete()
    commit()
