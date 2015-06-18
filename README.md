[![Build Status](https://travis-ci.org/kevindoole/fullstack-nanodegree-vm.svg?branch=master)](https://travis-ci.org/kevindoole/fullstack-nanodegree-vm)
[![Code Climate](https://codeclimate.com/github/kevindoole/fullstack-nanodegree-vm/badges/gpa.svg)](https://codeclimate.com/github/kevindoole/fullstack-nanodegree-vm)

Tournament
=============

Implementation of a Swiss-system tournament.
_v0.0.0.1 -- June 18, 2015_

## Swiss Pairing?
A [Swiss-system tournment](https://en.wikipedia.org/wiki/Swiss-system_tournament) pairs players based on their rankings from the previous rounds.

In this particular implementation, each player is paired with another player with an equal or nearly-equal win record, that is, a player adjacent to him or her in the standings.

## Features
- If both players score the same in their match, it is a draw and each player gets 1 point. Otherwise, the winner gets 3 points, the loser gets nothing.
- Rematches are avoided if at all possible.
- An odd number of players can compete. The player with the fewest points each round will get a "bye" worth three points. Only one bye is allowed per players per tournament.
- When two players have the same number of wins, they will be ranked by opponent match wins, the total number of wins by players they have played against.
- All matches will be saved for posterity. Simply create a new tournament when you're ready and the results will be kept separate from other tournaments.
- Players can be reused from one tournament to the next.

## Requirements
Python, Postgresql, psycopg2 OR you can use the included Vagrant box (see below)

## Usage
The basic workflow to running a tournament is:
1. Create a tournament by creating an instance of the Tournament class: `tournament = Tournament()`
2. Register players for you tournament: `tournament.register_player(name)`
3. Get pairings: `tournament.swiss_pairings()`
4. Have your players play their matches. Record the results:
```
player1 = (player1_id, player1_score)
player2 = (player2_id, player2_score)
tournament.report_match(player1, player2)
```
5. Once all your rounds have finished, execute `tournament.swiss_pairings()` again to determine matchups for the next round.
6. Continue for the necessary number of rounds:
| Number of Players | Number of Rounds   |
| ----------------- | ------------------ |
| 17–32 players     | 5 rounds of Swiss  |
| 33–64             | 6 rounds of Swiss  |
| 65–128            | 7 rounds of Swiss  |
| 129–226           | 8 rounds of Swiss  |
| 227–409           | 9 rounds of Swiss  |
| 410+              | 10 rounds of Swiss |

## Development environment
This package includes a [Vagrant](https://www.vagrantup.com/) development environment, in case you you don't have Python, Postgresql or psycopg2 available. You must have installed Vagrant to use it. [Download a package for your OS](https://www.vagrantup.com/downloads.html).

Once installed, clone this repo and run the VM.
```
$ git clone git@github.com:kevindoole/fullstack-nanodegree-vm.git
$ cd fullstack-nanodegree-vm/vagrant
$ vagrant up
```

Once installed, you can SSH into the VM and find the project files like so:
```
$ vagrant ssh
$ cd /vagrant/tournament
```

Install the database:
```
$ psql
$ \i tournament.sql
```

Run the tests: `python tournament_test.py`
