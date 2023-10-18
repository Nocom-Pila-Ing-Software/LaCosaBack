"""Defines 'game' endpoints
"""

import json
import time
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from lacosa.utils import find_card, find_game, find_player
from pony.orm import db_session
from lacosa.game.schemas import GameCreationRequest, GameStatus, PlayCardRequest
from lacosa.schemas import PlayerID, GameID
from lacosa.game.utils.game_creator import GameCreator
from .utils.deck import Deck
from lacosa.game.utils.game_status import GameStatusHandler
from lacosa.game.utils.game_actions import CardPlayer

game_router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, room_id: int, player_id: int):
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        await websocket.accept()
        self.active_connections[room_id].append((websocket, player_id, []))

    def disconnect(self, websocket: WebSocket, room_id: int):
        for connection in self.active_connections[room_id]:
            if connection[0] == websocket:
                self.active_connections[room_id].remove(connection)
                break

    async def save_message(self, websocket: WebSocket, room_id: int):
        for connection in self.active_connections[room_id]:
            if connection[0] == websocket:
                connection[2].append(await websocket.receive_text())
                break

    async def receive_message(self, websocket: WebSocket, room_id: int, command_to_receive: str):
        data = None
        for connection in self.active_connections[room_id]:
            if connection[0] == websocket:
                if len(connection[2]) > 0:
                    data = connection[2].pop(0)
                else:
                    data = await websocket.receive_text()

        while json.loads(data)["type"] != command_to_receive:
            await websocket.send_text(json.dumps({
                "type": "error",
                "payload": {
                    "message": f"Invalid command, expected {command_to_receive}"
                }
            }))
            data = await websocket.receive_text()
        return json.loads(data)["payload"]

    async def send_message(self, websocket: WebSocket, command_to_send: str, payload: dict):
        await websocket.send_text(json.dumps({
            "type": command_to_send,
            "payload": payload
        }))

    async def get_websocket(self, room_id: int, player_id: int):
        for connection in self.active_connections[room_id]:
            if connection[1] == player_id:
                return connection[0]
        return None

    async def broadcast_message(self, room_id: int, command_to_send: str, payload: dict):
        for connection in self.active_connections[room_id]:
            await self.send_message(connection[0], command_to_send, payload)


manager = ConnectionManager()


@game_router.websocket("/{room_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, player_id: int):
    with db_session:
        await manager.connect(websocket, room_id, player_id)
        try:
            game_status = GameStatusHandler(room_id)
            try:
                while True:
                    if game_status.get_response().playerPlayingTurn.playerID == player_id:
                        # Notify the player that it's their turn
                        await manager.send_message(websocket, "drawCard", {})

                        # The player draws a card
                        payload = await manager.receive_message(websocket, room_id, "drawCard")
                        Deck.draw_card(room_id, player_id)

                        # Notify the player of their hand and which cards are playable
                        await manager.send_message(websocket, "useCard", Deck.hand_info(player_id))

                        # The player select a card to play or discard
                        payload = await manager.receive_message(websocket, room_id, "useCard")
                        played_card_id = payload["cardID"]
                        if payload["isPlayed"]:

                            # Notify the player of the possible targets for the card they selected
                            await manager.send_message(websocket, "playCard", Deck.possible_targets(played_card_id, player_id))

                            # The player selects a target
                            payload = await manager.receive_message(websocket, room_id, "playCard")

                            # The target is notified of the card played and the player that played it and the possible defense cards to use
                            # target_id = payload["targetID"]
                            # websocket_target = await manager.get_websocket(room_id, target_id)
                            # await manager.send_message(websocket_target, "playCard", {
                            #     "defenseCards": Deck.possible_defense_cards(played_card_id, target_id),
                            #     "playerID": player_id,
                            #     "cardID": played_card_id
                            # })

                            # # The target selects a defense card
                            # payload = await manager.receive_command(websocket_target, "defend")
                            # if payload["isPlayed"]:
                            #     # FIXME: Execute defense

                            #     # All players are notified of the attack and the defense card played
                            #     manager.broadcast_message(room_id, "useCardResult", {
                            #         "discarded": False,
                            #         "attackResult": True,
                            #         "playerID": player_id,
                            #         "cardID": played_card_id,
                            #         "defenseCardID": payload["cardID"],
                            #         "targetID": target_id
                            #     })
                            # else:
                            # FIXME: Execute attack

                            # All players are notified of the attack
                            await manager.broadcast_message(room_id, "useCardResult", {
                                "discarded": False,
                                "attackResult": True,
                                "card": {
                                    "name": find_card(played_card_id).name,
                                    "id": played_card_id
                                },
                                "defenseCard": None,
                                "player": {
                                    "name": find_player(player_id).username,
                                    "id": player_id
                                },
                                "playerDefended": None
                            })
                        else:
                            # The player discards the card
                            Deck.discard_card(played_card_id, player_id)

                            # All players are notified of the discarded card
                            await manager.broadcast_message(room_id, "useCardResult", {
                                "discarded": True,
                                "attackResult": False,
                                "card": {
                                    "name": find_card(played_card_id).name,
                                    "id": played_card_id
                                },
                                "defenseCard": None,
                                "player": {
                                    "name": find_player(player_id).username,
                                    "id": player_id
                                },
                                "playerDefended": None
                            })

                        # The player ends their turn
                        game=find_game(room_id)

                        next_player = game.players.select(
                            lambda p: p.position == find_player(player_id).position + 1).first()
                        if next_player is None:
                            next_player = game.players.select(
                                lambda p: p.position == 1).first()
                        game.current_player = next_player.id
                                        

                    else:
                        await manager.save_message(websocket, room_id)

            except WebSocketDisconnect:
                manager.disconnect(websocket, room_id)
        except HTTPException as e:
            await websocket.send_text(json.dumps({
                "type": "error",
                "payload": {
                    "message": f"{e.detail}"
                }
            }))
            await websocket.close()
            manager.disconnect(websocket, room_id)


@game_router.post(path="", status_code=status.HTTP_201_CREATED)
async def create_game(creation_request: GameCreationRequest) -> GameID:
    with db_session:
        game_creator = GameCreator(creation_request)
        game_creator.create()
        response = game_creator.get_response()

    return response


# @game_router.put(path="/{room_id}/deal-card", status_code=status.HTTP_200_OK)
# async def draw_card(room_id: int, player_id: PlayerID) -> None:
#     with db_session:
#         Deck.draw_card(room_id, player_id.playerID)


@game_router.get(path="/{room_id}", status_code=status.HTTP_200_OK)
async def get_game_info(room_id) -> GameStatus:
    with db_session:
        status_handler = GameStatusHandler(room_id)
        response = status_handler.get_response()
        # FIXME: this is a bit ugly
        status_handler.delete_if_game_over(response)

    return response


# @game_router.put(path="/{room_id}/play-card", status_code=status.HTTP_200_OK)
# async def play_card(play_request: PlayCardRequest, room_id: int) -> None:
#     with db_session:
#         card_handler = CardPlayer(play_request, room_id)
#         card_handler.execute_action()
