import flask


def ok():
    return flask.make_response(flask.jsonify({"status": "OK"}), 200)


def unauthorized():
    return flask.make_response(flask.jsonify({"status": "UNAUTHORIZED"}), 401)


def not_found():
    return flask.make_response(flask.jsonify({"status": "NOT_FOUND"}), 404)


def internal_server_error():
    return flask.make_response(flask.jsonify({"status": "INTERNAL_SERVER_ERROR"}), 500)


def invalid_username():
    return flask.make_response(flask.jsonify(
        {
            "status": "INVALID_USERNAME",
            "data": "Username must be at most 32 chars and can only contain lowercase letters, numbers and underscores."
        }
    ), 400)


def invalid_email():
    return flask.make_response(flask.jsonify({"status": "INVALID_EMAIL"}), 400)


def username_taken():
    return flask.make_response(flask.jsonify({"status": "USERNAME_TAKEN"}), 400)


def email_taken():
    return flask.make_response(flask.jsonify({"status": "EMAIL_TAKEN"}), 400)


def too_big():
    return flask.make_response(flask.jsonify({"status": "TOO_BIG"}), 400)