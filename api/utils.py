import json
import functools

from aiohttp import web

from api.models import ServiceLog


pretty_json = functools.partial(json.dumps, indent=4)


def login_required(func):
    async def wrapper(request):
        if not request.user:
            await service_log(request)
            return web.json_response(
                {'Error': 'Auth required'}, status=401, dumps=pretty_json)
        return await func(request)
    return wrapper


async def service_log(request):
    ip_address = request.remote
    user = request.user
    user_id = getattr(user, 'id', None)
    await ServiceLog.create(user_id=user_id, ip_address=ip_address)
