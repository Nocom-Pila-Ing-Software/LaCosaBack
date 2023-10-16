from ..schemas import PlayCardRequest
from .card_effects import get_card_effect_function
import lacosa.utils as utils
import lacosa.game.utils.exceptions as exceptions
from lacosa.interfaces import ActionInterface
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter


class CardPlayer(ActionInterface):
    def __init__(self, play_request: PlayCardRequest, game_id: int, websockets: WebSocket) -> None:
        self.game = utils.find_game(game_id)
        self.player = utils.find_player(play_request.playerID)
        self.target_player = utils.find_player(play_request.targetPlayerID)
        self.card = utils.find_card(play_request.cardID)
        self.websocket = websockets
        self.handle_errors()

    async def execute_action(self, websocket: WebSocket) -> None:
        """
        Plays a card on the game

        Args:
        play_request (PlayCardRequest): Input data to validate
        game_id (int): The id of the game to validate
        """

        nombre_carta_que_defiende_el_efecto = "carta defensa"
        message = f"¿Quieres jugar la carta {nombre_carta_que_defiende_el_efecto}?"

        # Use the WebSocket to ask the target_player if they want to play the defense card
        await websocket.send_text(message)
        response = await websocket.receive_text()

        if not response == "Defenderse":
            effect_function = get_card_effect_function(self.card.name)
            effect_function(self.target_player, self.game)
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

        exceptions.validate_player_in_game(self.game, self.player)
        exceptions.validate_player_in_game(self.game, self.target_player)
        exceptions.validate_player_has_card(self.player, self.card.id)
        exceptions.validate_player_alive(self.target_player)
