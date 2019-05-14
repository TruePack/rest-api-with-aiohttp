import pytest
from gino.ext.aiohttp import Gino
from app import init


@pytest.fixture
async def client(aiohttp_client, loop):
    app, _, _ = await init(loop)

    db = Gino()

    db.init_app(
        app,
        config={
            "user": "postgres",
            "password": "",
            "database": "gino",
            "host": "postgres-test"})

    async with db.with_bind('postgresql://postgres@postgres-test/gino'):
        await db.gino.create_all()

    return await aiohttp_client(app)
