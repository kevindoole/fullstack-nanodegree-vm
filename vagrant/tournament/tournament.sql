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

CREATE TABLE byes (
    player_id     INTEGER REFERENCES players (id),
    tournament_id INTEGER REFERENCES tournaments (id),
    PRIMARY KEY   (player_id, tournament_id)
);

CREATE TABLE match_points (
    id            SERIAL PRIMARY KEY,
    tournament_id INTEGER REFERENCES tournaments (id),
    player_id     INTEGER REFERENCES players (id),
    opponent_id   INTEGER REFERENCES players (id),
    points        SMALLINT
);

CREATE VIEW standings AS
    SELECT p.id, p.name, COALESCE(sum(match_points.points),0) as points, count(match_points.player_id),
        (
            SELECT count(player_id)
                FROM match_points
                WHERE points = 3 AND player_id IN (
                    SELECT opponent_id FROM match_points WHERE player_id = p.id
                )
        ) AS omw, players_tournaments.tournament_id
    FROM players AS p
    LEFT JOIN match_points ON p.id = match_points.player_id
    LEFT JOIN players_tournaments ON p.id = players_tournaments.player_id
    GROUP BY players_tournaments.tournament_id, p.id
    ORDER BY points DESC, omw DESC;


CREATE VIEW last_place_without_bye AS
    SELECT id, standings.tournament_id
    FROM standings
    LEFT JOIN byes ON player_id = id AND byes.tournament_id = standings.tournament_id
    GROUP BY standings.tournament_id, id, points
    HAVING count(byes) = 0
    ORDER BY points
    LIMIT 1;