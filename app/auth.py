from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import PlainTextResponse
import ipaddress

ALLOWED_NETWORKS = [
    ipaddress.ip_network("127.0.0.1/32"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("192.168.1.0/24"),
]

class IPBlockerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        try:
            ip = ipaddress.ip_address(client_ip)
            if not any(ip in net for net in ALLOWED_NETWORKS):
                return PlainTextResponse("403 Forbidden: Access denied", status_code=403)
        except Exception:
            return PlainTextResponse("403 Forbidden: Invalid IP", status_code=403)
        return await call_next(request)

def is_logged_in(request: Request):
    return request.session.get("user")