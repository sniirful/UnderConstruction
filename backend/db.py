import os
import mysql.connector
import time

MYSQL_HOST = os.environ.get("MYSQL_HOST", "db")
MYSQL_USER = os.environ.get("MYSQL_USER", "social_user")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "social_password")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "social_network")


def escape_string(s: str) -> str:
    if s is None:
        return "NULL"
    return "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"


def get_connection() -> mysql.connector.pooling.PooledMySQLConnection | mysql.connector.connection.MySQLConnectionAbstract:
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )


def select_one(query: str) -> dict:
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result


def select_all(query: str) -> list[dict]:
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# TODO: inside app.py, check the return code
#       of the insert calls
def insert(query: str) -> int:
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    connection.commit()
    result = cursor.lastrowid
    cursor.close()
    connection.close()
    return result


def delete(query: str) -> None:
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


def update(query: str) -> int:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    connection.close()
    return affected_rows


def login(email: str, password: str) -> dict | None:
    return select_one(
        f"SELECT * FROM users WHERE email = {escape_string(email)} AND password = {escape_string(password)}"
    )


def register(id: int, username: str, email: str, password: str) -> dict | None:
    insert(
        f"INSERT INTO users (id, username, email, password) VALUES ({id}, {escape_string(username)}, {escape_string(email)}, {escape_string(password)})"
    )
    return select_one(f"SELECT * FROM users WHERE email = {escape_string(email)}")


def get_user_by_id(user_id: int) -> dict | None:
    return select_one(f"SELECT * FROM users WHERE id = {user_id}")


def get_user_by_email(email: str) -> dict | None:
    return select_one(f"SELECT * FROM users WHERE email = {escape_string(email)}")


def get_user_by_username(username: str) -> dict | None:
    return select_one(f"SELECT * FROM users WHERE username = {escape_string(username)}")


def set_user_profile_picture(user_id: int, profile_picture: str) -> None:
    return update(f"UPDATE users SET profile_picture = {escape_string(profile_picture)} WHERE id = {user_id}")


def set_user_fav_manga(user_id: int, fav_manga: str) -> None:
    return update(f"UPDATE users SET fav_manga = {escape_string(fav_manga)} WHERE id = {user_id}")


def set_user_fav_genres(user_id: int, fav_genres: str) -> None:
    return update(f"UPDATE users SET fav_genres = {escape_string(fav_genres)} WHERE id = {user_id}")


def set_user_css(user_id: int, css: str) -> None:
    return update(f"UPDATE users SET css = {escape_string(css)} WHERE id = {user_id}")


def follow_user(user_id: int, following_id: int) -> None:
    return insert(f"INSERT INTO follows (user_id, following_id) VALUES ({user_id}, {following_id})")


def unfollow_user(user_id: int, following_id: int) -> None:
    return delete(f"DELETE FROM follows WHERE user_id = {user_id} AND following_id = {following_id}")


def create_post(user_id: int, text: str) -> int:
    return insert(
        f"INSERT INTO posts (user_id, text, posted) VALUES ({user_id}, {escape_string(text)}, {int(time.time())})"
    )


def get_posts_home(user_id: int) -> list[dict]:
    return select_all(
        f"""
            SELECT
                p.id,
                p.user_id,
                u.username,
                u.profile_picture,
                p.posted,
                p.text,
                (EXISTS (SELECT 1 FROM likes WHERE user_id = {user_id} AND post_id = p.id)) as liked,
                (SELECT COUNT(1) FROM likes WHERE post_id = p.id) as like_count
            FROM
                posts p
            JOIN
                follows f ON f.user_id = {user_id} AND f.following_id = p.user_id
            JOIN
                users u ON p.user_id = u.id
            LEFT JOIN
                seen_posts sp ON p.id = sp.post_id AND sp.user_id = {user_id}
            WHERE
                p.user_id = f.following_id
            AND
                sp.post_id IS NULL
            ORDER BY
                p.posted DESC
            LIMIT 50
        """
    )


def get_posts_popular(user_id: int, filter_genres: list[str]) -> list[dict]:
    return select_all(
        f"""
            SELECT
                p.id,
                p.user_id,
                u.username,
                u.profile_picture,
                (EXISTS (SELECT 1 FROM follows WHERE user_id = {user_id} AND following_id = p.user_id)) as following,
                p.posted,
                p.text,
                (EXISTS (SELECT 1 FROM likes WHERE user_id = {user_id} AND post_id = p.id)) as liked,
                (SELECT COUNT(1) FROM likes WHERE post_id = p.id) as like_count
            FROM
                posts p
            JOIN
                users u ON p.user_id = u.id
            WHERE
                false
            {"".join([f" OR u.fav_genres LIKE '%{genre}%'" for genre in filter_genres]) if filter_genres else "OR true"}
            ORDER BY
                like_count / POWER(2, ({int(time.time())} - p.posted) / 1800) DESC, p.posted DESC
            LIMIT 50
        """
    )


def get_posts_new(user_id: int, filter_genres: list[str]) -> list[dict]:
    return select_all(
        f"""
            SELECT
                p.id,
                p.user_id,
                u.username,
                u.profile_picture,
                (EXISTS (SELECT 1 FROM follows WHERE user_id = {user_id} AND following_id = p.user_id)) as following,
                p.posted,
                p.text,
                (EXISTS (SELECT 1 FROM likes WHERE user_id = {user_id} AND post_id = p.id)) as liked,
                (SELECT COUNT(1) FROM likes WHERE post_id = p.id) as like_count
            FROM
                posts p
            JOIN
                users u ON p.user_id = u.id
            WHERE
                false
            {"".join([f" OR u.fav_genres LIKE '%{genre}%'" for genre in filter_genres]) if filter_genres else "OR true"}
            ORDER BY
                p.posted DESC
            LIMIT 50
        """
    )


def get_post_by_id(post_id: int) -> dict | None:
    return select_one(f"SELECT * FROM posts WHERE id = {post_id}")


def like_post(user_id: int, post_id: int) -> None:
    return insert(f"INSERT INTO likes (user_id, post_id) VALUES ({user_id}, {post_id})")


def unlike_post(user_id: int, post_id: int) -> None:
    return delete(f"DELETE FROM likes WHERE user_id = {user_id} AND post_id = {post_id}")


def mark_post_seen(user_id: int, post_id: int) -> None:
    return insert(f"INSERT INTO seen_posts (user_id, post_id) VALUES ({user_id}, {post_id})")


def unmark_post_seen(user_id: int, post_id: int) -> None:
    return delete(f"DELETE FROM seen_posts WHERE user_id = {user_id} AND post_id = {post_id}")

def send_message(user_id: int, recipient_id: int, message: str) -> None:
    return insert(
        f"INSERT INTO messages (from_id, to_id, message, sent) VALUES ({user_id}, {recipient_id}, {escape_string(message)}, {int(time.time())})"
    )

def get_messages(user_id: int, recipient_id: int) -> list[dict]:
    return select_all(
        f"""
            SELECT
                m.id,
                m.from_id,
                m.to_id,
                m.message,
                m.sent,
                m.picture,
                u.username,
                u.profile_picture
            FROM
                messages m
            JOIN
                users u ON m.to_id = u.id
            WHERE
                (m.from_id = {user_id} AND m.to_id = {recipient_id})
            OR
                (m.from_id = {recipient_id} AND m.to_id = {user_id})
            ORDER BY
                m.sent ASC
        """
    )

def get_chats(user_id) -> list[dict]:
    # Copilot actually made it work!
    return select_all(
        f"""
            SELECT
                u.id as recipient,
                u.username,
                u.profile_picture,
                (SELECT message FROM messages m2 WHERE ((m2.from_id = {user_id} AND m2.to_id = u.id) OR (m2.from_id = u.id AND m2.to_id = {user_id})) ORDER BY m2.sent DESC LIMIT 1) as message
            FROM
                users u
            WHERE
                u.id != {user_id} AND
                EXISTS (SELECT 1 FROM messages m3 
                        WHERE (m3.from_id = {user_id} AND m3.to_id = u.id) OR 
                              (m3.from_id = u.id AND m3.to_id = {user_id}))
            ORDER BY
                (SELECT sent FROM messages m4 
                 WHERE ((m4.from_id = {user_id} AND m4.to_id = u.id) OR (m4.from_id = u.id AND m4.to_id = {user_id}))
                 ORDER BY m4.sent DESC LIMIT 1) DESC
        """
    )
