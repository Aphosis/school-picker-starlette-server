from .mutation import mutation
from ....auth import hasher
from ....db import database
from ....sql import users
from ....validation import (
    CreateUserInput,
    UpdateUserInput,
    User,
)

# TODO: #1 Better type annotations for user resolvers


@mutation.field("createUser")
async def resolve_create_user(*_, input):
    data = CreateUserInput(**input)

    hashed_password = hasher.hash(data.password)
    query = users.insert()
    values = {
        "email": data.email,
        "hashed_password": hashed_password,
    }

    row = await database.execute(query, values)

    return User(id=row, email=data.email, hashed_password=hashed_password)


@mutation.field("updateUser")
async def resolve_update_user(*_, input):
    data = UpdateUserInput(**input)

    values = {}

    if data.password:
        hashed_password = hasher.hash(data.password)
        values["hashed_password"] = hashed_password

    if data.email:
        values["email"] = data.email

    query = (
        users.update()
        .where(users.c.id == data.id)
        .returning(users.c.id, users.c.email, users.c.hashed_password)
    )

    await database.execute(query, values)

    # TODO: #2 `returning` method does not seem to work,
    # so query the whole user from the database.
    query = users.select(users.c.id == data.id)
    row = await database.fetch_one(query)

    return User(**row)


@mutation.field("deleteUser")
async def resolve_delete_user(*_, id: int) -> bool:
    query = users.delete().where(users.c.id == id)
    await database.execute(query)
    return True
