from flask import redirect, session, make_response
from flask_http_middleware import BaseHTTPMiddleware

allowed_get = ["/login", "/register", "/ping"]
allowed_post = ["/login", "/register", "/put_backup_here"]


class AccessMiddleware(BaseHTTPMiddleware):
    def __init__(self, db):
        super().__init__()
        self.db = db

    def dispatch(self, request, call_next):
        if (request.method == "GET" and request.path.startswith('/static/')):
            return call_next(request)
        if (request.method == "GET" and request.path in allowed_get) or (request.method == "POST" and request.path in allowed_post):
            return call_next(request)
        if "user" in session and self.db.get_user_id(session["user"]) != False:
            return call_next(request)
        else:
            return redirect("/login")


class Access:
    def __init__(self, connector):
        self._connector = connector

    def is_admin(self, f):
        def decorator(*args, **kwargs):
            if not self._connector.db.get_user(session["user"])["admin"]:
                return make_response({"error": "Access denied"}, 403)
            return f(*args, **kwargs)

        decorator.__name__ = f.__name__
        return decorator
