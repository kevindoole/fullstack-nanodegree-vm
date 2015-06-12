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

def delete_matches():
    """Remove all the match records from the database."""
    run_query("TRUNCATE TABLE matches;", None, True)

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

def register_player(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    run_query("INSERT INTO players (name) values(%s);", (name,), True)

def player_standings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = connect()
    c = db.cursor()
    c.execute("""SELECT * FROM standings""")
    standings = c.fetchall()
    db.close()
    return standings

def report_match(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    run_query("""INSERT INTO matches (player_id, score)
        VALUES(%s, '1'), (%s, '0');""", (winner, loser,), True)

def swiss_pairings():
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
    standings = player_standings()
    pairings = []
    while len(standings):
        [player1, player2] = [standings.pop(), standings.pop()]
        [player1_id, player1_name, player2_id, player2_name] = [
            player1[0], player1[1], player2[0], player2[1]
        ]
        pairings.append((player1_id, player1_name, player2_id, player2_name))
    return pairings
