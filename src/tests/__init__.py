from models import db
db.bind(provider='sqlite', filename=':sharedmemory:', create_db=True)
db.generate_mapping(create_tables=True)