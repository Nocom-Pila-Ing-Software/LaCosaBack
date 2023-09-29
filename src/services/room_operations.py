from fastapi import HTTPException, status
from schemas.player import PlayerID, PlayerName
from pony.orm import db_session, commit
from models import WaitingRoom, Player

def create_player(player_name: PlayerName, room_ID: int) -> Player:
    # Crear un nuevo jugador y agregarlo a la base de datos
    player = Player(username=player_name, room=room_ID)
    commit()

    return player

def player_name_valid(player_name: PlayerName) -> None:
    # Validar que el playerName no esté vacío
        if not player_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player name cannot be empty"
            )
        
def player_exists_in_database(player: Player) -> None:
    # Verificar que el jugador se haya creado correctamente
    if player is None:
        print(player.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Player not created"
            )

def waiting_room_exists(room_ID: int) -> None:
    # Verificar que la sala exista
    if WaitingRoom.get(id=room_ID) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Room not found"
            )

def player_added_to_room(player: Player, room: WaitingRoom) -> None:
    # Verificar que el jugador se haya agregado correctamente a la sala
    if player not in room.players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Player not added to room"
            )