"""Application main module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import db
from api import api_router
from constants import DB_PROVIDER, PROJECT_DESCRIPTION, PROJECT_NAME
from settings import settings
from version import __API__VERSION

app = FastAPI(
    title=PROJECT_NAME,
    description=PROJECT_DESCRIPTION,
    version=__API__VERSION,
    root_path=settings.ROOT_PATH,
    debug=settings.DEBUG_MODE,
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/version")
async def version():
    """
    gets api version

    Returns
    -------
    Dict
        returns api version
    """
    return {"version": __API__VERSION}


# Including routers
app.include_router(api_router)

# Connecting to DB and creating tables
if __name__ == '__main__':
    db.bind(provider=DB_PROVIDER, filename=settings.DB_FILEANAME, create_db=True)
    db.generate_mapping(create_tables=True)
