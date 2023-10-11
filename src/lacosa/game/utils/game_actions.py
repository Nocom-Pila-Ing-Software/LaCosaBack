from fastapi import HTTPException
from ..schemas import PlayCardRequest
from .card_effects import apply_lanzallamas_effect
import lacosa.game.utils.utils as utils


class CardHandler:
    def __init__(self, play_request: PlayCardRequest, game_id: int):
        self.game = utils.find_game(game_id)
        self.player = utils.find_player(play_request.playerID)
        self.target_player = utils.find_player(play_request.targetPlayerID)
        self.card = utils.find_card(play_request.cardID)
        self.handle_errors()

    def play_card(self) -> None:
        """
        Plays a card on the game

        Args:
        play_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate
        """

        if self.card.name == "Lanzallamas":
            apply_lanzallamas_effect(self.target_player, self.game)

        self.player.cards.remove(self.card)
        self.game.cards.add(self.card)
        self.game.last_played_card = self.card

        self.game.current_player = self.get_next_player_id()

    def get_next_player_id(self):
        next_player = self.game.players.select(
            lambda p: p.position == self.player.position + 1).first()
        if next_player is None:
            next_player = self.game.players.select(
                lambda p: p.position == 1).first()
        return next_player.id

    @staticmethod
    def validate_player_in_game(player, game):
        if player.game != game:
            raise HTTPException(
                status_code=400,
                detail="Player is not in this game"
            )

    @staticmethod
    def validate_player_has_card(player, card_id):
        if not player.cards.filter(id=card_id).exists():
            raise HTTPException(
                status_code=400,
                detail="Player does not have that card"
            )

    @staticmethod
    def validate_player_alive(player):
        if not player.is_alive:
            raise HTTPException(
                status_code=400,
                detail="Player is dead"
            )

    def handle_errors(self) -> None:
        """
        Checks for errors in play_request and raises HTTPException if needed

        Args:
        play_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate

        Raises:
        HTTPException(status_code=400): If the player is not found or not is allowed to play
        HTTPException(status_code=404): If the game is not found
        """

        self.validate_player_in_game(self.player, self.game)
        self.validate_player_in_game(self.target_player, self.game)
        self.validate_player_has_card(self.player, self.card.id)
        self.validate_player_alive(self.target_player)
