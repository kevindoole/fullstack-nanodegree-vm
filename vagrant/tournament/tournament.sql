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

CREATE TABLE byes (
    player_id INTEGER PRIMARY KEY REFERENCES players (id)
);

CREATE TABLE match_points (
    id          SERIAL PRIMARY KEY,
    player_id   INTEGER REFERENCES players (id),
    opponent_id INTEGER REFERENCES players (id),
    points      SMALLINT
);

CREATE VIEW standings AS
    SELECT p.id, p.name, COALESCE(sum(match_points.points),0) as points, count(match_points.player_id),
        (
            SELECT count(player_id)
                FROM match_points
                WHERE points = 3 AND player_id IN (
                    SELECT opponent_id FROM match_points WHERE player_id = p.id
                )
        ) AS omw
    FROM players AS p
    LEFT JOIN match_points ON p.id = match_points.player_id
    GROUP BY p.id
    ORDER BY points desc, omw desc;


CREATE VIEW last_place_without_bye AS
    SELECT id
    FROM standings
    LEFT JOIN byes ON player_id = id
    GROUP BY id, points
    HAVING count(byes) = 0
    ORDER BY points
    LIMIT 1;