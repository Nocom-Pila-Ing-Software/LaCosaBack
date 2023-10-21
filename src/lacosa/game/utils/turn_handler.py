from models import Game, Player


def _get_next_position(current_player: Player, game: Game):
    alive_players = game.players.filter(lambda p: p.is_alive)
    next_position = current_player.position % len(alive_players) + 1
    return next_position


def get_next_player(game: Game, current_player: Player) -> Player:
    next_position = _get_next_position(current_player, game)

    next_player = game.players.select(
        lambda p: p.position == next_position
    ).first()

    return next_player


def increment_turn(game: Game, current_player: Player) -> None:
    next_player = get_next_player(game, current_player)
    game.current_player = next_player.id
