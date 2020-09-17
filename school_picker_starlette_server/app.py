from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.config import Config
from ariadne.asgi import GraphQL

from .graphql import schema

config = Config(".env")


def create_app(config: Config) -> Starlette:
    debug = config("DEBUG", cast=bool, default=False)
    app = Starlette(
        debug=debug,
        routes=[
            Mount("/graphql", GraphQL(schema=schema, debug=debug)),
        ],
    )
    return app


app = create_app(config)
