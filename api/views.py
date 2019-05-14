from datetime import datetime, timedelta
from aiohttp import web, ClientSession
from aiohttp_apispec import docs, request_schema, response_schema
from asyncpg.exceptions import UniqueViolationError
import jwt
from api.models import User, Joke
from api.utils import pretty_json, login_required
from api.schemas import (
    DeleteJokeResponseSchema, UserRegistrationRequestSchema, JokeRequestSchema,
    UserLoginRequestSchema, JokeResponseSchema, UserLoginResponseSchema,
    UserRegistrationResponseSchema)


JWT_EXP_DELTA_SECONDS = 3600
JWT_ALGORITHM = 'HS256'
JWT_SECRET = 'secret'
GET_JOKE_URL = 'https://geek-jokes.sameerkumar.website/api'


@docs(tags=["Authorization"],
      summary="Return JWT token for authentication user.",
      description=(
          "Accept POST request and return token if credentials is valid."))
@request_schema(UserLoginRequestSchema(strict=True))
@response_schema(UserLoginResponseSchema, 200)
async def login(request):
    data = request['data']
    username = data['username']
    raw_password = data['password']
    user = await User.query.where(User.username == username).gino.first()

    if user is not None:
        password_match = user.verify_password(raw_password)
    if user is None or not password_match:
        return web.json_response({'Error': 'Wrong credentials'}, status=400)

    payload = {
        'user_id': user.id,
        'exp': datetime.now() + timedelta(seconds=JWT_EXP_DELTA_SECONDS)}
    jwt_token = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)

    return web.json_response(
        {'token': jwt_token.decode('utf-8')}, dumps=pretty_json)


@docs(tags=["Authorization"],
      summary="Registration for new user.",
      description=(
          "Accept POST request and return new user's id. "
          "After you can authorization with username and password on /login."))
@request_schema(UserRegistrationRequestSchema(strict=True))
@response_schema(UserRegistrationResponseSchema, 201)
async def registration(request):
    data = request['data']
    username = data['username']
    raw_password = data['password']
    stored_password = User.hash_password(raw_password)

    try:
        user = await User.create(username=username, password=stored_password)
    except UniqueViolationError:
        return web.json_response(
            {'Error': 'Username already taken'}, dumps=pretty_json, status=400)

    return web.json_response(
        {'id': user.id, 'username': username}, dumps=pretty_json, status=201)


@docs(tags=["Jokes"],
      summary="Return all user's jokes.",
      description="Accept GET request and return user's jokes.")
@response_schema(JokeResponseSchema(many=True), 200)
@login_required
async def jokes_list(request):
    jokes_qs = await Joke.query.where(
        Joke.user_id == request.user.id).gino.all()
    jokes_schema = JokeResponseSchema(many=True)
    jokes_json, errors = jokes_schema.dump(jokes_qs)

    return web.json_response({'jokes': jokes_json}, dumps=pretty_json)


@docs(tags=["Jokes"],
      summary="Will generate random joke.",
      description=(
          "Accept POST request and generate new joke. "
          "Jokes are unique for each user."))
@response_schema(JokeResponseSchema())
@login_required
async def joke_create(request):
    async with ClientSession() as session:
        joke = None
        while not joke:
            async with session.get(GET_JOKE_URL) as resp:
                text_of_joke = await resp.json()
                try:
                    joke = await Joke.create(
                            text=text_of_joke, user_id=request.user.id)
                except UniqueViolationError:
                    print(
                        "Joke's API return not unique joke "
                        f"for {request.user.username}. "
                        "Trying again...")

    joke_schema = JokeResponseSchema()
    joke_json, errors = joke_schema.dump(joke)

    return web.json_response(joke_json, dumps=pretty_json, status=201)


@docs(tags=["Jokes"],
      summary="Return joke by ID.",
      description="Accept GET request for joke return joke object in json.")
@response_schema(JokeResponseSchema(), 200)
@login_required
async def joke_detail(request):
    joke_id = int(request.match_info['id'])
    joke = await Joke.get(joke_id)

    if joke is None:
        raise web.HTTPNotFound()
    if not joke.is_joke_owner(request.user):
        return web.json_response(
            {"Error": "This is not your joke."}, dumps=pretty_json, status=403)

    joke_schema = JokeResponseSchema()
    joke_json, errors = joke_schema.dump(joke)

    return web.json_response(joke_json, dumps=pretty_json)


@docs(tags=["Jokes"],
      summary="Update joke by ID.",
      description="Accept PATCH request for joke and update joke's text.")
@request_schema(JokeRequestSchema(strict=True))
@response_schema(JokeResponseSchema(), 200)
@login_required
async def joke_update(request):
    joke_id = int(request.match_info['id'])
    data = request["data"]
    new_text = data["text"]

    joke = await Joke.get(joke_id)

    if joke is None:
        raise web.HTTPNotFound()
    if not joke.is_joke_owner(request.user):
        return web.json_response(
            {"Error": "This is not your joke."}, dumps=pretty_json, status=403)

    await joke.update(text=new_text).apply()

    joke_schema = JokeResponseSchema()
    joke_json, errors = joke_schema.dump(joke)

    return web.json_response(joke_json, dumps=pretty_json)


@docs(tags=['Jokes'],
      summary='Delete joke by ID.',
      description='Accept DELETE request for joke and delete it.')
@response_schema(DeleteJokeResponseSchema(), code=204)
@login_required
async def joke_delete(request):
    """
    I dont know why, but this endpoint return nothing, if everything ok.
    Its raise exception Response <type of response> not prepared.
    Also other web.json_responses responses correctly.
    I've tried other aiohttp versions, without result.
    I think its aiohttp bug.
    ¯\_(ツ)_/¯
    """
    joke_id = int(request.match_info['id'])
    joke = await Joke.get(joke_id)
    if joke is None:
        raise web.HTTPNotFound()
    if not joke.is_joke_owner(request.user):
        return web.json_response(
            {'Error': 'This is not your joke.'}, dumps=pretty_json, status=403)

    await joke.delete()

    return web.json_response(
        {'Message': 'Successfuly deleted'}, dumps=pretty_json, status=204)
