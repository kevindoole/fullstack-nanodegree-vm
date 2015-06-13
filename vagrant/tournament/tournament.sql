-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

\c tournament;

CREATE TABLE players (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(30)
);

CREATE TABLE byes (
    player_id INTEGER PRIMARY KEY REFERENCES players (id)
);

CREATE TABLE matches (
    id        SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players (id),
    points    SMALLINT
);

CREATE VIEW standings AS
    SELECT p.id, p.name,
    (
        SELECT COALESCE(sum(matches.points),0)
        FROM matches
        WHERE matches.player_id = p.id
    ) as points, count(matches.player_id)
    FROM players AS p
    LEFT JOIN matches ON p.id = matches.player_id
    GROUP BY p.id
    ORDER BY points desc;
