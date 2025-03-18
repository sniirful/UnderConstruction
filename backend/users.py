import os
import re
import flask
import secrets

import db

cookies: dict[str, int] = {
    os.environ.get('ADMIN_COOKIE', 'admin_cookie'): 1
}


def is_valid_username(username: str, maxlength: int, allowed_chars: str) -> bool:
    if len(username) > maxlength:
        return False

    for char in username:
        if char not in allowed_chars:
            return False

    return True


def is_valid_email(email: str) -> bool:
    return not re.match(r"[^@]+@[^@]+\.[^@]+", email) is None


def get_user_flask(request: flask.Request) -> dict | None:
    user_id = request.cookies.get('user_id')
    if user_id is None:
        return None

    user_id = cookies.get(user_id)
    if user_id is None:
        return None

    return db.get_user_by_id(user_id)


def set_user_flask(response: flask.Response, user_id: int) -> None:
    cookie = secrets.token_hex(16)
    cookies[cookie] = user_id
    response.set_cookie('user_id', cookie, httponly=True)
