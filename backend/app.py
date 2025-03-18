import flask
import flask_socketio
import secrets
import time
import random

import db
import users
import responses

app = flask.Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)
socketio = flask_socketio.SocketIO(app, cors_allowed_origins="*")

cookies: dict[str, int] = {}


@app.route('/api/login', methods=['POST'])
def login():
    data = flask.request.json
    email = data.get('email')
    password = data.get('password')

    if not users.is_valid_email(email):
        user = None
    else:
        user = db.login(email, password)

    if user:
        response = responses.ok()
        users.set_user_flask(response, user['id'])
        return response
    else:
        return responses.not_found()


@app.route('/api/register', methods=['POST'])
def register():
    data = flask.request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not users.is_valid_username(username, 32, "abcdefghijklmnopqrstuvwxyz1234567890_"):
        return responses.invalid_username()

    if not users.is_valid_email(email):
        return responses.invalid_email()

    if db.get_user_by_username(username):
        return responses.username_taken()

    if db.get_user_by_email(email):
        return responses.email_taken()

    user = db.register(random.randint(0, 999999999), username, email, password)

    if user:
        response = responses.ok()
        users.set_user_flask(response, user['id'])
        return response
    else:
        # This should not happen...
        return responses.internal_server_error()


@app.route('/api/profile', methods=['GET'])
def get_profile():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    if flask.request.args.get('id') is not None and user['id'] == 1:
        target_user = db.get_user_by_id(int(flask.request.args['id']))
        if not target_user:
            return responses.not_found()
        user = target_user

    user['fav_genres'] = user['fav_genres'].split(',') if user['fav_genres'] else []
    return flask.jsonify({"status": "OK", "data": user})


@app.route('/api/profile/picture', methods=['POST'])
def set_profile_picture():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.json
    profile_picture = data.get('profile_picture')
    if len(profile_picture) > 2 * 1024 * 1024:  # 2 MiB
        return responses.too_big()

    # TODO: must validate the picture first...

    db.set_user_profile_picture(user['id'], profile_picture)
    return responses.ok()


@app.route('/api/profile/manga', methods=['POST'])
def set_profile_fav_manga():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.json
    fav_manga = data.get('fav_manga')

    db.set_user_fav_manga(user['id'], fav_manga)
    return responses.ok()


@app.route('/api/profile/genres', methods=['POST'])
def set_profile_fav_genres():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.json
    fav_genres = data.get('fav_genres')

    db.set_user_fav_genres(user['id'], ','.join(fav_genres) if isinstance(fav_genres, list) else "")
    return responses.ok()


@app.route('/api/profile/css', methods=['POST'])
def set_profile_css():
    user = users.get_user_flask(flask.request)
    if not user or user['id'] != 1:
        return responses.unauthorized()

    data = flask.request.json
    target_user_id = data.get('id')
    css = data.get('css')

    if not db.get_user_by_id(target_user_id):
        return responses.not_found()

    db.set_user_css(target_user_id, css)
    return responses.ok()


@app.route('/api/profile/follow', methods=['POST'])
def follow():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.json
    target_user_id = data.get('id')

    if not db.get_user_by_id(target_user_id):
        return responses.not_found()

    db.follow_user(user['id'], target_user_id)
    return responses.ok()


@app.route('/api/profile/unfollow', methods=['POST'])
def unfollow():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.json
    target_user_id = data.get('id')

    if not db.get_user_by_id(target_user_id):
        return responses.not_found()

    db.unfollow_user(user['id'], target_user_id)
    return responses.ok()


@app.route('/api/post', methods=['POST'])
def post():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.json
    text = data.get('text')

    db.create_post(user['id'], text)
    return responses.ok()


@app.route('/api/posts/home', methods=['GET'])
def get_posts_home():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    posts = db.get_posts_home(user['id'])
    return flask.jsonify({
        "status": "OK",
        "data": [{
            "id": post['id'],
            "poster": {
                "id": post['user_id'],
                "username": post['username'],
                "profile_picture": post['profile_picture'],
            },
            "posted": post['posted'],
            "text": post['text'],
            "liked": bool(post['liked']),
            "likes": post['like_count'],
        } for post in posts]
    })


@app.route('/api/posts/popular', methods=['GET'])
def get_posts_popular():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    filter_genres = flask.request.args.get('genres')
    posts = db.get_posts_popular(user['id'], filter_genres.split(',') if filter_genres else [])
    return flask.jsonify({
        "status": "OK",
        "data": [{
            "id": post['id'],
            "poster": {
                "id": post['user_id'],
                "username": post['username'],
                "following": bool(post['following']),
                "profile_picture": post['profile_picture'],
            },
            "posted": post['posted'],
            "text": post['text'],
            "liked": bool(post['liked']),
            "likes": post['like_count'],
        } for post in posts]
    })


@app.route('/api/posts/new', methods=['GET'])
def get_posts_new():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    filter_genres = flask.request.args.get('genres')
    posts = db.get_posts_new(user['id'], filter_genres.split(',') if filter_genres else [])
    return flask.jsonify({
        "status": "OK",
        "data": [{
            "id": post['id'],
            "poster": {
                "id": post['user_id'],
                "username": post['username'],
                "following": bool(post['following']),
                "profile_picture": post['profile_picture'],
            },
            "posted": post['posted'],
            "text": post['text'],
            "liked": bool(post['liked']),
            "likes": post['like_count'],
        } for post in posts]
    })


@app.route('/api/posts/seen', methods=['POST'])
def mark_post_seen():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.json
    post_id = data.get('id')

    if not db.get_post_by_id(post_id):
        return responses.not_found()

    db.mark_post_seen(user['id'], post_id)
    return responses.ok()


@app.route('/api/posts/unseen', methods=['POST'])
def unmark_post_seen():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.json
    post_id = data.get('id')

    if not db.get_post_by_id(post_id):
        return responses.not_found()

    db.unmark_post_seen(user['id'], post_id)
    return responses.ok()


@app.route('/api/posts/like', methods=['POST'])
def like_post():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.json
    post_id = data.get('id')

    if not db.get_post_by_id(post_id):
        return responses.not_found()

    db.like_post(user['id'], post_id)
    return responses.ok()


@app.route('/api/posts/unlike', methods=['POST'])
def unlike_post():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.json
    post_id = data.get('id')

    if not db.get_post_by_id(post_id):
        return responses.not_found()

    db.unlike_post(user['id'], post_id)
    return responses.ok()


@app.route('/api/chats', methods=['GET'])
def get_chats():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    return flask.jsonify(db.get_chats(user['id']))


@app.route('/api/chats/messages', methods=['GET'])
def get_messages():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.args
    recipient_id = int(data.get('id'))

    return flask.jsonify(db.get_messages(user['id'], recipient_id))


@app.route('/api/chats/user', methods=['GET'])
def get_user():
    user = users.get_user_flask(flask.request)
    if not user:
        return responses.unauthorized()

    data = flask.request.args
    recipient_id = int(data.get('id'))

    recipient = db.get_user_by_id(recipient_id)
    if recipient is None:
        return responses.not_found()

    return flask.jsonify({
        "id": recipient['id'],
        "username": recipient['username'],
        "profile_picture": recipient['profile_picture']
    })


connected_users = {}


@socketio.on('connect')
def handle_connect():
    user = users.get_user_flask(flask.request)
    if not user:
        return


@socketio.on('room')
def handle_room(id: str):
    user = users.get_user_flask(flask.request)
    if not user:
        return

    room = f"{user['id']}.{id}"
    connected_users[user['id']] = id
    flask_socketio.join_room(room)


@socketio.on('message')
def handle_message(to_id: int, message: str):
    user = users.get_user_flask(flask.request)
    if not user:
        return

    db.send_message(user['id'], to_id, message)

    recipient = connected_users[to_id]
    if recipient is None:
        return

    socketio.emit('message', {
        'from_id': user['id'],
        'to_id': to_id,
        'message': message,
        'username': user['username'],
        'profile_picture': user['profile_picture'],
        'sent': int(time.time())
    }, to=f"{to_id}.{recipient}")


@socketio.on('disconnect')
def handle_disconnect():
    user = users.get_user_flask(flask.request)
    if not user:
        return

    room = f"{user['id']}.{connected_users[user['id']]}"
    flask_socketio.close_room(room)
    del connected_users[user['id']]


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
