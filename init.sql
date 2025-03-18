CREATE DATABASE IF NOT EXISTS underconstruction;
USE underconstruction;

CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(255) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,
    fav_manga       TEXT     DEFAULT (''),
    fav_genres      TEXT     DEFAULT (''),
    css             TEXT     DEFAULT (''),
    profile_picture LONGTEXT DEFAULT NULL
);

CREATE TABLE follows (
    user_id      INT NOT NULL,
    following_id INT NOT NULL,
    PRIMARY KEY (user_id, following_id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (following_id) REFERENCES users (id)
);

CREATE TABLE posts (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT    NOT NULL,
    text    TEXT   NOT NULL,
    posted  BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE likes (
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (post_id) REFERENCES posts (id)
);

CREATE TABLE seen_posts (
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    PRIMARY KEY (user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (post_id) REFERENCES posts (id)
);

CREATE TABLE messages (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    from_id  INT    NOT NULL,
    to_id    INT    NOT NULL,
    message  TEXT   NOT NULL,
    picture  TEXT,
    sent     BIGINT NOT NULL,
    FOREIGN KEY (from_id) REFERENCES users (id),
    FOREIGN KEY (to_id) REFERENCES users (id)
);

CREATE TABLE flag (
    flag VARCHAR(57) PRIMARY KEY
);

INSERT INTO users (username, email, password) VALUES ('admin', 'admin', 'admin');
INSERT INTO flag (flag) VALUES ('KSUS{this_is_not_exactly_a_filter_is_it_f83hD32Dkc3hNEey}');