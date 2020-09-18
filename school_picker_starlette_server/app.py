from ariadne.asgi import GraphQL
from ariadne.graphql import GraphQLSchema
from databases import Database
from starlette.applications import Starlette
from starlette.config import Config
from starlette.routing import Mount

from .config import config
from .db import database
from .graphql import schema


def create_app(
    config: Config,
    database: Database,
    schema: GraphQLSchema,
) -> Starlette:
    debug = config("DEBUG", cast=bool, default=False)

    app = Starlette(
        debug=debug,
        routes=[
            Mount("/graphql", GraphQL(schema=schema, debug=debug)),
        ],
        on_startup=[database.connect],
        on_shutdown=[database.disconnect],
    )

    return app


app = create_app(config, database, schema)
