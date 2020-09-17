from ariadne import QueryType


query = QueryType()


@query.field("hello")
async def resolve_hello(*_, name=None):
    return f"Hello {name or 'guest'}"
