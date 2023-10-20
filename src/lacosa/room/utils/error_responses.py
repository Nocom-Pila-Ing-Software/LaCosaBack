from fastapi import status


error_responses = {
    "400": {status.HTTP_400_BAD_REQUEST: {"description": "Invalid request"}},
    "404": {status.HTTP_404_NOT_FOUND: {"description": "Room not found"}},
    "400&404": {status.HTTP_404_NOT_FOUND: {"description": "Room not found"},
                status.HTTP_400_BAD_REQUEST: {"description": "Invalid request"}}
}
