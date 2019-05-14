import jwt
from aiohttp import web

from api.models import User
from api.views import JWT_ALGORITHM, JWT_SECRET
from api.utils import service_log

@web.middleware
async def auth_middleware(request, handler):
    request.user = None
    jwt_token = request.headers.get('Authorization', None)

    if jwt_token:
        if jwt_token.startswith('Bearer '):
            jwt_token = jwt_token[7:]
        try:
            payload = jwt.decode(
                jwt_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            # Create log without user.id.
            await service_log(request)
            return web.json_response(
                {'message': 'Token is invalid'}, status=400)

        request.user = await User.get(payload['user_id'])
        # Create log with user.id.
        await service_log(request)
    return await handler(request)
