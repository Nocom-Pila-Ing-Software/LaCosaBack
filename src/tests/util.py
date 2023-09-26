from models import db


def setup_test_db():
    db.bind(provider="sqlite", filename=":sharedmemory:", create_db=True)
    db.generate_mapping(create_tables=True)
    return db