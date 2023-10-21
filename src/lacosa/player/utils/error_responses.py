from fastapi import status


error_responses = {
    "403&404": {status.HTTP_404_NOT_FOUND: {"description": "Player not found"},
                status.HTTP_403_FORBIDDEN: {"description": "Player is not in a game"}},
    "400&403&404": {status.HTTP_400_BAD_REQUEST: {"description": "Player does not have the card"},
                    status.HTTP_404_NOT_FOUND: {"description": "Player not found"},
                    status.HTTP_403_FORBIDDEN: {"description": "Player is not in a game"}},
}
