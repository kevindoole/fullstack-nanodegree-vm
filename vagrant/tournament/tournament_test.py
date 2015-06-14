from tournament import *

def test_delete_matches():
    delete_match_points()
    print "1. Old matches can be deleted."


def test_delete():
    delete_match_points()
    delete_players()
    print "2. Player records can be deleted."


def test_count():
    delete_match_points()
    delete_players()
    c = count_players()
    if c == '0':
        raise TypeError(
            "count_players() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, count_players should return zero.")
    print "3. After deleting, count_players() returns zero."


def test_register():
    delete_match_points()
    delete_players()
    register_player("Chandra Nalaar")
    c = count_players()
    if c != 1:
        raise ValueError(
            "After one player registers, count_players() should be 1.")
    print "4. After registering a player, count_players() returns 1."


def test_register_count_delete():
    delete_match_points()
    delete_players()
    register_player("Markov Chaney")
    register_player("Joe Malik")
    register_player("Mao Tsu-hsi")
    register_player("Atlanta Hope")
    c = count_players()
    if c != 4:
        raise ValueError(
            "After registering four players, count_players should be 4.")
    delete_players()
    c = count_players()
    if c != 0:
        raise ValueError("After deleting, count_players should return zero.")
    print "5. Players can be registered and deleted."


def test_standings_before_matches():
    delete_match_points()
    delete_players()
    register_player("Melpomene Murray")
    register_player("Randy Schwartz")
    standings = player_standings()
    if len(standings) < 2:
        raise ValueError("Players should appear in player_standings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 5:
        raise ValueError("Each player_standings row should have five columns.")
    [(id1, name1, wins1, matches1, omw1), (id2, name2, wins2, matches2, omw2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def test_report_matches():
    delete_match_points()
    delete_players()
    register_player("Bruno Walton")
    register_player("Boots O'Neal")
    register_player("Cathy Burton")
    register_player("Diane Grant")
    standings = player_standings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    report_match((id1,1), (id2,0))
    report_match((id3,1), (id4,1))
    standings = player_standings()
    for (i, n, p, m, omw) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i == id1 and p != 3:
            raise ValueError("Each match winner should have three points recorded.")
        if i == id2 and p != 0:
            raise ValueError("Each match loser should have zero points recorded.")
        elif i in (id3, id4) and p != 1:
            raise ValueError("Each draw player should have one point recorded.")
    print "7. After a match, players have updated standings."


def test_pairings():
    delete_match_points()
    delete_players()
    register_player("Twilight Sparkle")
    register_player("Fluttershy")
    register_player("Applejack")
    register_player("Pinkie Pie")
    standings = player_standings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    report_match((id1,1), (id2,0))
    report_match((id3,1), (id4,0))
    pairings = swiss_pairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swiss_pairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."

def test_byes():
    delete_match_points()
    delete_players()
    register_player("Bruno Walton")
    register_player("Boots O'Neal")
    register_player("Cathy Burton")
    standings = player_standings()
    [id1, id2, id3] = [row[0] for row in standings]
    report_match((id1,1), (id2,1))
    pairings = swiss_pairings()
    if len(pairings) != 1:
        raise ValueError(
            "There should only be pairings for an even number of players")
    standings = player_standings()
    for (i, n, p, m, omw) in standings:
        if i == id3 and p != 3:
            raise ValueError(
                "The lowest rank player in round one should get a bye.")
        if i in (id1, id2) and p != 1:
            raise ValueError("Tied players should have 1 point each")
    try:
        bye(id3)
    except psycopg2.IntegrityError:
        pass
    else:
        raise ValueError("Players should be able to have more than one bye.")
    print "9. The lowest ranked player gets a bye for 3 points."

def test_bye_fallback():
    standings = player_standings()
    [bye_player_id, id2, id3] = [row[0] for row in standings]
    report_match((id2,2), (id3,1))
    report_match((id2,1), (id3,2))
    pairings = swiss_pairings()
    [(pid1, pname1, pid2, pname2)] = pairings
    if bye_player_id not in (pid1, pid2):
        raise ValueError("A player cannot have a bye twice.")
    print "10. No player can have more than one bye."

def test_opponent_match_wins_count():
    delete_match_points()
    delete_players()
    register_player("Twilight Sparkle")
    register_player("Fluttershy")
    register_player("Applejack")
    standings = player_standings()
    [id1, id2, id3] = [row[0] for row in standings]
    report_match((id1,1), (id2,0))
    report_match((id1,1), (id3,0))
    report_match((id1,1), (id2,0))
    standings = player_standings()
    for (i, n, p, m, omw) in standings:
        if i == id1 and omw != 0:
            raise ValueError("id1 should have 0 omw.")
        if i == id2 and omw != 3:
            raise ValueError("id2 should have 3 omw.")
        if i == id3 and omw != 3:
            raise ValueError("id3 should have 3 omw.")
    print "11. Opponent match wins accumulate correctly."

def test_opponent_match_wins_rank():
    delete_match_points()
    delete_players()
    register_player("Twilight Sparkle")
    register_player("Fluttershy")
    register_player("Applejack")
    register_player("Pinkie Pie")
    standings = player_standings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    report_match((id1,1), (id3,0)) # id1 3p, 0omw   |   id2 0p, 1omw
    report_match((id2,1), (id4,1))
    report_match((id3,1), (id1,1))
    report_match((id1,1), (id3,0))

    pairings = swiss_pairings()
    [(pid1, pname1, pid2, pname2),(pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]),frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "Tied players should be ranked by opponent match wins.")
    print "12. Tied players should be ranked by opponent match wins."

if __name__ == '__main__':
    test_delete_matches()
    test_delete()
    test_count()
    test_register()
    test_register_count_delete()
    test_standings_before_matches()
    test_report_matches()
    test_pairings()
    test_byes()
    test_bye_fallback()
    test_opponent_match_wins_count()
    test_opponent_match_wins_rank()
    print "Success!  All tests pass!"


