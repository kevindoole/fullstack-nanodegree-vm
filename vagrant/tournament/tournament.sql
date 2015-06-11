-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE DATABASE tournament;
\c tournament;

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30)
);

CREATE TABLE matches (
    winner INTEGER REFERENCES players (id),
    loser INTEGER REFERENCES players (id),
    PRIMARY KEY (winner, loser)
);
