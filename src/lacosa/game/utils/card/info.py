import json
from lacosa import utils
import lacosa.game.utils.exceptions as exceptions
from lacosa.interfaces import ResponseInterface
from lacosa.player.schemas import (
    UsabilityActionResponse,
    UsabilityActionInfoCard,
    UsabilityResponse,
    UsabilityInfoCard,
    TargetsResponse,
    TargetsInfo,
)
from fastapi import status
from models import Event
from pony.orm import select
from settings import settings


class CardTargetsInformer(ResponseInterface):
    def __init__(self, player_id: int, card_id: int):
        self.player = utils.find_player(player_id, status.HTTP_404_NOT_FOUND)
        self.card = utils.find_card(card_id, status.HTTP_404_NOT_FOUND)
        self.handle_errors()

    def get_response(self) -> TargetsResponse:
        """
        Returns the information of which players can be targeted/attacked with the card

        Returns:
        TargetsResponse: The players information
        """

        return TargetsResponse(targets=self.get_targets_info())

    def get_targets_info(self) -> list:
        """
        Returns the information of which players can be targeted/attacked with the card

        Returns:
        list: The players information
        """

        targets = []
        if self.get_target(self.card.name) == "adjacent":
            targets = self.get_adjacent_players()
        elif self.get_target(self.card.name) == "global":
            targets = self.get_global_players()
        elif self.get_target(self.card.name) == "self":
            targets = [TargetsInfo(
                playerID=self.player.id,
                name=self.player.username
            )]

        return targets

    def get_target(self, card_name: str) -> str:
        """
        Returns the type of the card
        """
        with open(settings.DECK_CONFIG_PATH) as config_file:
            config = json.load(config_file)

        targets = config["cards"][card_name]["target"]

        return targets if targets != "No" else None

    def get_adjacent_players(self) -> list:
        """
        Returns the adjacent players
        """
        players = []
        for player in self.player.game.players.sort_by(lambda p: p.id):
            if player != self.player:
                before_position = self.player.position - 1
                after_position = self.player.position + 1
                total_positions = len(
                    select(p for p in self.player.game.players if p.is_alive is True)[:])
                if self.player.position == 1:
                    before_position = total_positions
                if self.player.position == total_positions:
                    after_position = 1
                if player.position == before_position or player.position == after_position:
                    players.append(TargetsInfo(
                        playerID=player.id,
                        name=player.username
                    ))

        return players

    def get_global_players(self) -> list:
        """
        Returns all players that can be targeted with the card (Not obstacules/quarentine)
        """

        players = []
        for player in self.player.game.players.sort_by(lambda p: p.id):
            if player != self.player and player.is_alive is True:
                players.append(TargetsInfo(
                    playerID=player.id,
                    name=player.username
                ))

        return players

    def handle_errors(self) -> None:
        """
        Checks for errors and raises HTTPException if needed
        """

        exceptions.validate_player_in_game(
            None, self.player, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_alive(self.player)
        exceptions.validate_correct_type(
            self.card, "action")
