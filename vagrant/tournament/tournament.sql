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

DROP VIEW matches_players;
CREATE VIEW matches_players AS
    SELECT id, name, score
    FROM players
    JOIN matches ON players.id = matches.player_id
    ORDER BY matches.score DESC;