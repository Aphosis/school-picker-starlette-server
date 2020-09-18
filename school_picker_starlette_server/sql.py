from sqlalchemy import Column, Integer, MetaData, String, Table

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", String, unique=True),
    Column("hashed_password", String),
)

token_blacklist = Table(
    "token_blacklist",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("jti", String, unique=True),
)
