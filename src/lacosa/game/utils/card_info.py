import json
from pathlib import Path
from lacosa import utils
from lacosa.game.utils.deck import Deck
import lacosa.game.utils.exceptions as exceptions
from lacosa.interfaces import ResponseInterface
from lacosa.player.schemas import UsabilityActionResponse, UsabilityActionInfoCard, UsabilityResponse, UsabilityInfoCard, TargetsResponse, TargetsInfo
from fastapi import status
from models import Event
from pony.orm import select


class CardUsabilityInformer(ResponseInterface):
    def __init__(self, player_id: int):
        self.player = utils.find_player(player_id, status.HTTP_404_NOT_FOUND)
        self.handle_errors()

    def get_response(self) -> UsabilityActionResponse:
        """
        Returns the information of which cards can be played or discarded by the player

        Returns:
        UsabilityInfoResponse: The cards information
        """

        return UsabilityActionResponse(cards=self.get_cards_info())

    def get_cards_info(self) -> list:
        """
        Returns the information of which cards can be played or discarded by the player

        Returns:
        list: The cards information
        """

        cards_info = []
        amount_infectado_cards_in_hand = 0
        for card in self.player.cards:
            if card.name == "infectado":
                amount_infectado_cards_in_hand += 1

        for card in self.player.cards:
            playable = True
            discardable = True
            if card.name == "infectado" or card.name == "La cosa" or self.get_card_type(card.name) == "defense":
                playable = False

            if card.name == "La cosa" or (card.name == "infectado" and amount_infectado_cards_in_hand == 1 and self.player.role == "infected"):
                discardable = False

            cards_info.append(UsabilityActionInfoCard(
                cardID=card.id,
                name=card.name,
                description=card.description,
                playable=playable,
                discardable=discardable
            ))
        return cards_info

    def get_card_type(self, card_name: str) -> str:
        """
        Returns the type of the card
        """
        config_path = Path(__file__).resolve().parent.parent / \
            'utils' / 'config_deck.json'

        with open(config_path) as config_file:
            config = json.load(config_file)

        return config["cards"][card_name]["type"]

    def handle_errors(self) -> None:
        """
        Checks for errors and raises HTTPException if needed
        """

        exceptions.validate_player_in_game(
            None, self.player, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_alive(self.player)


class CardDefenseInformer(ResponseInterface):
    def __init__(self, player_id: int, card_id: int):
        self.player = utils.find_player(player_id, status.HTTP_404_NOT_FOUND)
        self.card = utils.find_card(card_id, status.HTTP_404_NOT_FOUND)
        self.handle_errors()

    def get_response(self) -> UsabilityResponse:
        """
        Returns the information of which cards can be used to defend against the card played by the attacker

        Returns:
        UsabilityResponse: The cards information
        """

        return UsabilityResponse(cards=self.get_cards_info())

    def get_cards_info(self) -> list:
        """
        Returns the information of which cards can be used to defend against the card played by the attacker

        Returns:
        list: The cards information
        """

        cards_info = []
        # Get the cards that only are usable if the player is the target of the trade event (and only in a trade event)
        if self.card is None:
            event = select(e for e in Event if e.type == "trade" and (e.player1 == self.player or e.player2 == self.player) and e.is_completed == False).first()
            # Verify if the player is the target of the trade event and not the trader generating the event
            if event is not None and event.player2 == self.player:
                for card in self.player.cards:
                    if card.name == "No, gracias":
                        cards_info.append(UsabilityInfoCard(
                            cardID=card.id,
                            name=card.name,
                            description=card.description,
                            usable=True
                        ))
        else:
            # Cards that can be used to defend against the card (actions card) played by the attacker
            for card in self.player.cards:
                if card.name in self.get_cards_that_defend(self.card.name):
                    cards_info.append(UsabilityInfoCard(
                        cardID=card.id,
                        name=card.name,
                        description=card.description,
                        usable=True
                    ))

        return sorted(cards_info, key=lambda card: card.cardID)

    def get_cards_that_defend(self, card_name: str) -> str:
        """
        Returns the type of the card
        """
        config_path = Path(__file__).resolve().parent.parent / \
            'utils' / 'config_deck.json'

        with open(config_path) as config_file:
            config = json.load(config_file)

        return config["cards"][card_name]["defensible_by"]

    def handle_errors(self) -> None:
        """
        Checks for errors and raises HTTPException if needed
        """

        exceptions.validate_player_in_game(
            None, self.player, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_alive(self.player)
        if self.card is not None:
            exceptions.validate_correct_type(
                self.card, "action")

class CardTradeInformer(ResponseInterface):
    def __init__(self, player_id: int):
        self.player = utils.find_player(player_id, status.HTTP_404_NOT_FOUND)
        self.target = utils.find_target_in_trade_event(player_id)
        self.handle_errors()

    def get_response(self) -> UsabilityResponse:
        """
        Returns the information of which cards can be selected to trade with the player

        Returns:
        UsabilityResponse: The cards information
        """

        return UsabilityResponse(cards=self.get_cards_info())

    def get_cards_info(self) -> list:
        """
        Returns the information of which cards can be selected to trade with the player

        Returns:
        list: The cards information
        """

        amount_infectado_cards_in_hand = 0
        for card in self.player.cards:
            if card.name == "infectado":
                amount_infectado_cards_in_hand += 1

        cards_info = []
        for card in self.player.cards:
            usable = True
            if card.name == "La cosa":
                usable = False
            if card.name == "infectado" and amount_infectado_cards_in_hand == 1 and self.player.role == "infected":
                usable = False
            if card.name == "infectado" and self.target.role == "infected":
                usable = False
            if card.name == "infectado" and self.target.role != "human" and self.player.role == "the thing":
                usable = False
            if card.name == "infectado" and self.player.role == "human":
                usable = False

            cards_info.append(UsabilityInfoCard(
                cardID=card.id,
                name=card.name,
                description=card.description,
                usable=usable
            ))

        return cards_info

    def handle_errors(self) -> None:
        """
        Checks for errors and raises HTTPException if needed
        """

        exceptions.validate_player_in_game(
            None, self.player, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_in_game(
            None, self.target, status.HTTP_400_BAD_REQUEST)
        exceptions.validate_player_alive(self.player)
        exceptions.validate_player_alive(self.target)


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

        return targets

    def get_target(self, card_name: str) -> str:
        """
        Returns the type of the card
        """
        config_path = Path(__file__).resolve().parent.parent / \
            'utils' / 'config_deck.json'

        with open(config_path) as config_file:
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
                    select(p for p in self.player.game.players if p.is_alive == True)[:])
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
            if player != self.player and player.is_alive == True:
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
