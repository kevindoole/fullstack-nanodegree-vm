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

CREATE TABLE matches (
    id        SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players (id),
    score     SMALLINT
);

CREATE VIEW standings AS
    SELECT p.id, p.name,
    (
        SELECT count(matches.player_id)
        FROM matches
        WHERE matches.player_id = p.id
        AND matches.score = '1'
    ) as wins, count(matches.player_id)
    FROM players AS p
    LEFT JOIN matches ON p.id = matches.player_id
    GROUP BY p.id
    ORDER BY wins desc;
