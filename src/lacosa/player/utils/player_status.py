from fastapi import HTTPException
from lacosa.player.schemas import PlayerResponse
from schemas.schemas import PlayerID, CardID, CardInfo
from models import Player, Card, db
from typing import List


def check_player_exists(player_id: PlayerID) -> None:
    """
    Checks if a player exists on the database

    Args:
    player_id (PlayerID): Input data to validate

    Raises:
    HTTPException(status_code=404): If the player ID doesn't exist in database
    """

    player = Player.get(id=player_id)
    if player is None:
        raise HTTPException(
            status_code=404, detail="Player ID doesn't exist"
        )


def check_card_exists(card_id: CardID) -> None:
    """
    Checks if a card exists on the database

    Args:
    card_id (CardID): Input data to validate

    Raises:
    HTTPException(status_code=404): If the card ID doesn't exist in database
    """

    card = Card.get(id=card_id)
    if card is None:
        raise HTTPException(
            status_code=404, detail="Card ID doesn't exist"
        )


def get_list_hand_player(player_id: PlayerID) -> List[CardInfo]:
    """
    Get the list of cards of a player

    Args:
    player_id (PlayerID): Input data to validate

    Returns:
    list[CardInfo]: The list of cards of the player
    """

    player = Player.get(id=player_id)

    check_player_exists(player_id)

    list_hand = []
    for card in player.cards:
        list_hand.append(get_card_data(card))

    list_hand.sort(key=lambda x: x.cardID)

    return list_hand


def get_card_data(card) -> CardInfo:
    """
    Get the data of a card

    Args:
    card (Card): The card to get the data from

    Returns:
    CardInfo: The data of the card
    """

    check_card_exists(card.id)
    return CardInfo(
        cardID=card.id,
        name=card.name,
        description=card.description
    )


def get_player_info(player_id: PlayerID) -> PlayerResponse:
    """
    Get the info of a player

    Args:
    player_id (PlayerID): Input data to validate

    Returns:
    PlayerResponse: The info of the player
    """

    player = Player.get(id=player_id)

    check_player_exists(player_id)

    return PlayerResponse(
        hand=get_list_hand_player(player_id),
        role=player.role,
        is_alive=player.is_alive
    )


def delete_player(player_id: PlayerID) -> None:
    """
    Delete a player from the database

    Args:
    player_id (PlayerID): Input data to validate

    Raises:
    HTTPException(status_code=404): If the player ID doesn't exist in database
    """

    check_player_exists(player_id)

    player = Player.get(id=player_id)

    db.delete(player)
    db.commit()
