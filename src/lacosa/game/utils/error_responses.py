from fastapi import status


error_responses = {
    "404": {status.HTTP_404_NOT_FOUND: {"description": "Game not found"}},
    "400&403": {status.HTTP_400_BAD_REQUEST: {"description": "Invalid request"},
                status.HTTP_403_FORBIDDEN: {"description": "Player not has permission to execute this action"}},
    "400&403&404": {status.HTTP_400_BAD_REQUEST: {"description": "Invalid request"},
                    status.HTTP_403_FORBIDDEN: {"description": "Player not has permission to execute this action"},
                    status.HTTP_404_NOT_FOUND: {"description": "Game not found"}},
}
