from ariadne import QueryType

from ...db import database
from ...sql import users
from ...validation import User


query = QueryType()


@query.field("users")
async def resolve_users(*_):
    query = users.select()
    rows = await database.fetch_all(query)
    results = [User(**row) for row in rows]
    return results


@query.field("user")
async def resolve_user(*_, id):
    query = users.select(users.c.id == id)
    row = await database.fetch_one(query)
    result = User(**row)
    return result
