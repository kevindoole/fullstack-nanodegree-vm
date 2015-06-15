"""Implementation of a Swiss-system tournament."""

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def run_query(query, query_params=None, commit=False):
    """Connect to the DB and run a query."""
    db = connect()
    c = db.cursor()
    c.execute(query, query_params)
    if commit == True:
        db.commit()
    db.close()

def delete_match_points():
    """Remove all the match records from the database."""
    run_query("TRUNCATE TABLE match_points;", None, True)

def delete_players():
    """Remove all the player records from the database."""
    run_query("TRUNCATE TABLE players CASCADE;", None, True)

def count_players():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    c.execute("SELECT count(*) FROM players;")
    count = c.fetchone()
    db.close()
    return count[0]

def new_tournament():
    run_query("INSERT into tournaments DEFAULT VALUES;", None, commit=True)

def latest_record(table):
    db = connect()
    c = db.cursor()
    c.execute("SELECT id FROM " + table + " ORDER BY id desc LIMIT 1;")
    record = c.fetchone()
    db.close()
    return record[0]


class Tournament:

    def __init__(self):
        new_tournament()
        self.id = latest_record('tournaments')

    def register_player(self, name):
        """Adds a player to the tournament database.
        Args:
          name: the player's full name (need not be unique).
        """
        run_query("INSERT INTO players (name) values(%s);", (name,), True)
        player_id = latest_record('players')
        run_query("""INSERT INTO players_tournaments (player_id, tournament_id)
                        values(%s,%s);""", (player_id,self.id), True)

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
        db = connect()
        c = db.cursor()
        c.execute("""SELECT * FROM standings WHERE tournament_id = %s""",
            (self.id,))
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

        results = (player1_id, player1_points, player2_id, self.id, player2_id,
                    player2_points, player1_id, self.id)
        run_query("""INSERT INTO match_points (player_id, points, opponent_id,
            tournament_id) VALUES(%s, %s, %s, %s), (%s, %s, %s, %s);""", results, True)

    def which_player_can_bye(self, standings):
        db = connect()
        c = db.cursor()
        c.execute("SELECT id FROM last_place_without_bye WHERE tournament_id = %s;", (self.id,))
        bye_player = c.fetchone()
        db.close()
        bye_player_id = bye_player[0]
        i = 0
        for i, (id, n, p, m, omw, t_id) in enumerate(standings):
            if id == bye_player_id:
                return i
            i+=1

    def player_opponents(self, player_id):
        db = connect()
        c = db.cursor()
        c.execute("SELECT opponent_id FROM match_points WHERE player_id = %s AND tournament_id = %s",
            (player_id, self.id))
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
                player = standings.pop(bye_player_key)
                self.bye(player[0])
                continue

            player1 = standings.pop(0)
            player2 = None
            for i, (id, n, p, m, omw, t_id) in enumerate(standings):
                if player1[0] not in self.player_opponents(id):
                    player2 = standings.pop(i)
                    break

            if player2 == None:
                player2 = standings.pop(0)

            [player1_id, player1_name, player2_id, player2_name] = [
                player1[0], player1[1], player2[0], player2[1]
            ]
            pairings.append((player1_id, player1_name, player2_id, player2_name))
        return pairings

    def bye(self, player_id):
        run_query("INSERT INTO byes values(%s, %s);", (player_id, self.id), True)
        run_query("""INSERT INTO match_points (player_id, points)
            VALUES(%s, %s);""", (player_id, 3), True)