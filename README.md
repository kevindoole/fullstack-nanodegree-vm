[![Build Status](https://travis-ci.org/kevindoole/fullstack-nanodegree-vm.svg?branch=master)](https://travis-ci.org/kevindoole/fullstack-nanodegree-vm)
[![Code Climate](https://codeclimate.com/github/kevindoole/fullstack-nanodegree-vm/badges/gpa.svg)](https://codeclimate.com/github/kevindoole/fullstack-nanodegree-vm)

Tournament
=============

Implementation of a Swiss-system tournament.

## Swiss Pairing?
A [Swiss-system tournment](https://en.wikipedia.org/wiki/Swiss-system_tournament) pairs players based on their rankings from the previous rounds.

In this particular implementation, each player is paired with another player with an equal or nearly-equal win record, that is, a player adjacent to him or her in the standings. Given 16 players are registered for a tournment, then we will see four rounds. The winner will have a perfect 4-0 record.

## Usage
To run a tournament, select an even number of players for round one. Register them by name with `register_player(name)`.

As the results of your first round of matches come in, use `report_match(winner_id, loser_id)` to save the result.

Once all your round one matches have completed, use `swiss_pairings()` to generate a list of player pairings for round two.

Repeat until you have a winner...

## Development environment
This package includes a [Vagrant](https://www.vagrantup.com/) development environment, just for fun. You need to have Vagrant installed to use it. [Download a package for your OS](https://www.vagrantup.com/downloads.html).

Once installed, clone this repo and run the VM.
```
git clone git@github.com:kevindoole/fullstack-nanodegree-vm.git
cd fullstack-nanodegree-vm/vagrant
vagrant up
```

Once installed, you can SSH into the VM like so:
```
vagrant ssh
```

