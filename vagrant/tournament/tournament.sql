-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP DATABASE tournament;
CREATE DATABASE tournament;

\c tournament;

CREATE TABLE players (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(30)
);

CREATE TABLE tournaments (
    id SERIAL PRIMARY KEY
);

CREATE TABLE players_tournaments (
    player_id     INTEGER REFERENCES players (id),
    tournament_id INTEGER REFERENCES tournaments (id),
    PRIMARY KEY   (player_id, tournament_id)
);

CREATE TABLE player_points (
    id            SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments (id),
    player_id     INTEGER REFERENCES players (id),
    opponent_id   INTEGER REFERENCES players (id),
    points        SMALLINT
);

CREATE VIEW standings AS
    SELECT p.id, p.name, COALESCE(sum(player_points.points),0) as points, count(player_points.player_id),
        (
            SELECT count(player_id)
            FROM player_points
            WHERE points = 3 AND player_id IN (SELECT opponent_id FROM player_points WHERE player_id = p.id)
        ) AS omw, players_tournaments.tournament_id,
        array(SELECT opponent_id FROM player_points WHERE player_id = p.id) as opponents
    FROM players AS p
    LEFT JOIN player_points ON p.id = player_points.player_id
    LEFT JOIN players_tournaments ON p.id = players_tournaments.player_id
    GROUP BY players_tournaments.tournament_id, p.id
    ORDER BY points DESC, omw DESC;
