import asyncio
import pathlib

from aiohttp import web
from gino.ext.aiohttp import Gino
from aiohttp_apispec import validation_middleware, setup_aiohttp_apispec

import api.routes
import api.models
from api.middlewares import auth_middleware

PROJ_ROOT = pathlib.Path(__file__).parent.parent


async def init_db():
    await api.models.main()


async def init(loop):
    # Setup app.
    app = web.Application()

    # Setup routes
    for route in api.routes.routes:
        app.router.add_route(*route)

    # Setup DB connection
    await init_db()
    db = Gino()
    db.init_app(
        app,
        config={
            "user": "postgres",
            "password": "",
            "database": "gino",
            "host": "postgres"})

    # Setup middlewares
    middlewares = [
        db, validation_middleware, auth_middleware]
    app.middlewares.extend(middlewares)

    # Setup api_spec
    setup_aiohttp_apispec(
        app=app,
        title="Joke's API documentation",
        version='v1',
        url="/api/v1/docs/swagger.json",
        swagger_path="/api/v1/docs/")
    host = "0.0.0.0"
    port = 80
    return app, host, port


def main():
    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init(loop))
    web.run_app(app, host=host, port=port)


# Run app
if __name__ == '__main__':
    main()