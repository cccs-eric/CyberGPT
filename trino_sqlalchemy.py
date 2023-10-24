from sqlalchemy import create_engine
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.sql.expression import select, text
from trino.auth import OAuth2Authentication
import logging 
import http

# logging.basicConfig(level=logging.DEBUG)
# http.client.HTTPConnection.debuglevel = 1

# engine = create_engine("trino://trino.hogwarts.u.azure.chimera.cyber.gc.ca:443/system")
engine = create_engine(
"trino://trino.hogwarts.u.azure.chimera.cyber.gc.ca:443/system",
    connect_args={
        "auth": OAuth2Authentication(),
        "http_scheme": "https",
    }
)
connection = engine.connect()

rows = connection.execute(text("SHOW catalogs")).fetchall()

print(f"Got rows: {rows}")
# or using SQLAlchemy schema
# nodes = Table(
#     'nodes',
#     MetaData(schema='runtime'),
#     autoload=True,
#     autoload_with=engine
# )
# rows = connection.execute(select(nodes)).fetchall()

# ./trino --server https://trino.hogwarts.u.azure.chimera.cyber.gc.ca:443 --catalog hogwartsu --external-authentication --user Eric.Ladouceur@cyber.gc.ca