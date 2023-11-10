from typing import List
from models import Card, Player
from pony.orm import commit


def show_cards_to_players(cards: List[Card], players: List[Player]):
    for player in players:
        player.shown_cards = cards
    commit()
