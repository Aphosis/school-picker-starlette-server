import os
from ariadne import load_schema_from_path, make_executable_schema

from .resolvers.query import query

type_defs = load_schema_from_path(os.path.join(os.path.dirname(__file__), "typedefs"))
types = [query]

schema = make_executable_schema(type_defs, *types)
