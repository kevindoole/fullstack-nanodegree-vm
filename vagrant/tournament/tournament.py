"""Implementation of a Swiss-system tournament."""
# pylint: good-names=db,c

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    db = psycopg2.connect("dbname=tournament")
    cursor = db.cursor()
    return [db, cursor]

def commit_query(query, query_params=None):
    """Connect to the DB and run a query."""
    [db, c] = connect()
    c.execute(query, query_params)
    db.commit()
    db.close()

def delete_player_points():
    """Remove all the match records from the database."""
    commit_query("TRUNCATE TABLE player_points;")

def delete_players():
    """Remove all the player records from the database."""
    commit_query("TRUNCATE TABLE players CASCADE;")

def count_players():
    """Returns the number of players currently registered for all tournaments."""
    [db, c] = connect()
    c.execute("SELECT count(*) FROM players;")
    count = c.fetchone()
    db.close()
    return count[0]

class Tournament(object):
    """Keeps track of players, byes, matches and standings in order to generate
    Swiss Pairings for a tournament."""

    def __init__(self):
        [db, c] = connect()
        c.execute("INSERT into tournaments DEFAULT VALUES RETURNING id;")
        new_tournament_id = c.fetchone()[0]
        db.commit()
        db.close()
        self.tournament_id = new_tournament_id

    def register_player(self, name_or_id):
        """Adds a player to the tournament database.

        Args:
          name_or_id: the player's full name (need not be unique), or an existing players.id
          to reuse a player from an earlier tournament.
        """
        [db, c] = connect()

        is_player_id = isinstance( name_or_id, int );
        if ( is_player_id ):
            player_id = name_or_id
            c.execute("SELECT id FROM players WHERE id = %s", (player_id,))
            if not c.fetchone():
                raise ValueError("Unknown player id")
        else:
            name = name_or_id
            c.execute("INSERT INTO players (name) VALUES(%s) RETURNING id;", (name,))
            player_id = c.fetchone()[0]

        c.execute("""INSERT INTO players_tournaments (player_id, tournament_id)
                        VALUES(%s,%s);""", (player_id, self.tournament_id))
        db.commit()
        db.close()

    def player_standings(self):
        """Returns a list of the players and their win records, sorted by wins.

        The first entry in the list should be the player in first place, or a player
        tied for first place if there is currently a tie.

        Returns:
          A list of tuples, each of which contains (id, name, wins, matches):
            id: the player's unique id (assigned by the database)
            name: the player's full name (as registered)
            points: the number of points the player has
            matches: the number of matches the player has played
        """
        [db, c] = connect()
        c.execute("SELECT * FROM standings WHERE tournament_id = %s", (self.tournament_id,))
        standings = c.fetchall()
        db.close()
        return standings

    def report_match(self, player1, player2):
        """Records the outcome of a single match between two players.

        Args:
          player1:  (id, points)
          player2:  (id, points)
        """
        # winner gets 3 points, draw both get 1, loser gets none
        [player1_id, player2_id] = [player1[0], player2[0]]
        if player1[1] > player2[1]:
            [player1_points, player2_points] = [3, 0]
        elif player1[1] == player2[1]:
            player1_points = player2_points = 1
        else:
            [player1_points, player2_points] = [0, 3]

        results = (player1_id, player1_points, player2_id, self.tournament_id, player2_id,
                   player2_points, player1_id, self.tournament_id)
        commit_query("""INSERT INTO player_points (player_id, points, opponent_id,
            tournament_id) VALUES(%s, %s, %s, %s), (%s, %s, %s, %s);""", results)

    def which_player_can_bye(self, standings):
        """Provides id for the lowest ranking player who has not yet had a bye.

        Args:
            standings: see player_standings()

        Returns:
            the index in standings representing the player who can bye"""
        [db, c] = connect()
        c.execute("""SELECT id FROM last_place_without_bye
            WHERE tournament_id = %s;""", (self.tournament_id,))
        bye_player = c.fetchone()
        db.close()
        bye_player_id = bye_player[0]
        i = 0
        for i, (player_id, _, _, _, _, _) in enumerate(standings):
            if player_id == bye_player_id:
                return i
            i += 1

    def player_opponents(self, player_id):
        """Collects a list of opponents player_id has played against in the
        current tournament.

        Args:
            player_id: the id of the player of whom to find opponents

        Returns:
            list of player ids
        """
        [db, c] = connect()
        c.execute("""SELECT opponent_id FROM player_points WHERE player_id = %s
            AND tournament_id = %s""", (player_id, self.tournament_id))
        opponents = c.fetchall()
        db.close()
        return [x[0] for x in opponents]


    def swiss_pairings(self):
        """Returns a list of pairs of players for the next round of a match.

        Assuming that there are an even number of players registered, each player
        appears exactly once in the pairings.  Each player is paired with another
        player with an equal or nearly-equal win record, that is, a player adjacent
        to him or her in the standings.

        Returns:
          A list of tuples, each of which contains (id1, name1, id2, name2)
            id1: the first player's unique id
            name1: the first player's name
            id2: the second player's unique id
            name2: the second player's name
        """
        standings = self.player_standings()
        pairings = []
        while len(standings):
            if len(standings) % 2 == 1:
                bye_player_key = self.which_player_can_bye(standings)
                player_id = standings.pop(bye_player_key)[0]
                self.bye(player_id)
                continue

            player1 = standings.pop(0)
            player2 = None
            for i, (player_id, _, _, _, _, _) in enumerate(standings):
                if player1[0] not in self.player_opponents(player_id):
                    player2 = standings.pop(i)
                    break

            # If player2 is still None, we were not able to find an opponent
            # that's not a rematch, so we make do with a rematch.
            if not player2:
                player2 = standings.pop(0)

            [player1_id, player1_name, player2_id, player2_name] = [
                player1[0], player1[1], player2[0], player2[1]
            ]
            pairings.append((player1_id, player1_name, player2_id, player2_name))
        return pairings

    def bye(self, player_id):
        """Records a bye for a player.

        Args:
            player_id: the id of the player who's getting a bye"""
        [db, c] = connect()
        c.execute("INSERT INTO byes VALUES(%s, %s);", (player_id, self.tournament_id))
        c.execute("INSERT INTO player_points (player_id, points) VALUES(%s, %s);", (player_id, 3))
        db.commit()
        db.close()
