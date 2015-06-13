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

CREATE TABLE match_points (
    id        SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players (id),
    points    SMALLINT
);

CREATE VIEW standings AS
    SELECT p.id, p.name,
    (
        SELECT COALESCE(sum(match_points.points),0)
        FROM match_points
        WHERE match_points.player_id = p.id
    ) as points, count(match_points.player_id)
    FROM players AS p
    LEFT JOIN match_points ON p.id = match_points.player_id
    GROUP BY p.id
    ORDER BY points desc;

CREATE VIEW last_place_without_bye AS
    SELECT id
    FROM standings
    LEFT JOIN byes ON player_id = id
    GROUP BY id, points
    HAVING count(byes) = 0
    ORDER BY points
    LIMIT 1;