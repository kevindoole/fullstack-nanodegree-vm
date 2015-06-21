"""Tests tournament module"""
# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=wildcard-import

from tournament import *

tournament = Tournament()


def delete_matches_players():
    "Truncates players and player_points tables"
    delete_player_points()
    delete_players()


def test_delete_matches():
    "Truncates player_points table"
    delete_player_points()
    print "1. Old matches can be deleted."


def register_players(count):
    "Registers `count` players in the global tournament"
    for i in range(count):
        tournament.register_player("player" + `i`)


def test_delete():
    delete_matches_players()
    print "2. Player records can be deleted."


def test_count():
    delete_matches_players()
    c = count_players()
    if c == '0':
        raise TypeError(
            "count_players() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, count_players should return zero.")
    print "3. After deleting, count_players() returns zero."


def test_register():
    delete_matches_players()
    register_players(1)
    c = count_players()
    if c != 1:
        raise ValueError(
            "After one player registers, count_players() should be 1.")
    print "4. After registering a player, count_players() returns 1."


def test_register_count_delete():
    delete_matches_players()
    register_players(4)
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
    delete_matches_players()
    register_players(2)
    standings = tournament.player_standings()
    if len(standings) < 2:
        raise ValueError("Players should appear in player_standings even "
                         "before they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 7:
        raise ValueError(
            "Each player_standings row should have seven columns.")
    [(_, name1, wins1, matches1, _, _, _),
     (_, name2, wins2, matches2, _, _, _)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["player0", "player1"]):
        raise ValueError("Registered players' names should appear in "
                         "standings, even if they have no matches played.")
    print "6. Newly registered players are in the standings with no matches."


def test_report_matches():
    delete_matches_players()
    register_players(4)
    standings = tournament.player_standings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    tournament.report_match((id1, 1), (id2, 0))
    tournament.report_match((id3, 1), (id4, 1))
    standings = tournament.player_standings()
    for (i, _, p, m, _, _, _) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i == id1 and p != 3:
            raise ValueError(
                "Each match winner should have three points recorded.")
        elif i == id2 and p != 0:
            raise ValueError(
                "Each match loser should have zero points recorded.")
        elif i in (id3, id4) and p != 1:
            raise ValueError(
                "Each draw player should have one point recorded.")
    print "7. After a match, players have updated standings."


def test_pairings():
    delete_matches_players()
    register_players(4)
    standings = tournament.player_standings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    tournament.report_match((id1, 1), (id2, 0))
    tournament.report_match((id3, 1), (id4, 0))
    pairings = tournament.swiss_pairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swiss_pairings should return two pairs.")
    [(pid1, _, pid2, _), (pid3, _, pid4, _)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


def test_byes():
    delete_matches_players()
    register_players(3)
    standings = tournament.player_standings()
    [id1, id2, id3] = [row[0] for row in standings]
    tournament.report_match((id1, 1), (id2, 1))
    pairings = tournament.swiss_pairings()
    if len(pairings) != 1:
        raise ValueError(
            "There should only be pairings for an even number of players")
    standings = tournament.player_standings()
    for (i, _, p, _, _, _, _) in standings:
        if i == id3 and p != 3:
            raise ValueError("The lowest rank player in round one should get "
                             "a bye for 3 points.")
    print "9. A lowest ranked player gets a bye for 3 points only once."


def test_bye_fallback():
    # Continues from the previous test.
    standings = tournament.player_standings()
    # The first ranked player had a bye.
    [bye_player_id, id2, id3] = [row[0] for row in standings]
    tournament.report_match((id2, 2), (id3, 1))
    tournament.report_match((id2, 1), (id3, 2))
    # Bye player is in last place again.
    pairings = tournament.swiss_pairings()
    [(pid1, _, pid2, _)] = pairings
    if bye_player_id not in (pid1, pid2):
        raise ValueError(
            "Another player should get a bye before anyone repeats.")
    print "10. No player can have more than one bye."


def test_opponent_match_wins_count():
    delete_matches_players()
    register_players(3)
    standings = tournament.player_standings()
    [id1, id2, id3] = [row[0] for row in standings]
    tournament.report_match((id1, 1), (id2, 0))
    tournament.report_match((id1, 1), (id3, 0))
    tournament.report_match((id1, 1), (id2, 0))
    standings = tournament.player_standings()
    for (i, _, _, _, omw, _, _) in standings:
        if i == id1 and omw != 0:
            raise ValueError("id1 should have 0 omw.")
        if i == id2 and omw != 3:
            raise ValueError("id2 should have 3 omw.")
        if i == id3 and omw != 3:
            raise ValueError("id3 should have 3 omw.")
    print "11. Opponent match wins accumulate correctly."


def test_opponent_match_wins_rank():
    delete_matches_players()
    register_players(6)
    standings = tournament.player_standings()
    [id1, id2, id3, id4, id5, id6] = [row[0] for row in standings]
    tournament.report_match((id1, 1), (id2, 0))
    tournament.report_match((id3, 1), (id4, 0))
    tournament.report_match((id5, 1), (id6, 0))

    # Fudge the numbers a bit to get the specific pairings we need to test.
    query = "UPDATE player_points SET points = 0 WHERE player_id = %s"
    params = (id3,)
    commit_query(query, params)

    query = """UPDATE player_points
               SET opponent_id = %s
               WHERE player_id in (%s,%s)"""
    params = (id6, id3, id4)
    commit_query(query, params)
    # id1 = 3p/0omw, id5 = 3/0
    # id2 = 0/1, id6 = 0/1
    # id3 = 0/0, id4 = 0/0

    pairings = tournament.swiss_pairings()
    [(pid1, _, pid2, _), (pid3, _, pid4, _), (pid5, _, pid6, _)] = pairings
    correct_pairs = set([frozenset([id1, id5]), frozenset([id2, id6]),
                         frozenset([id3, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4]),
                        frozenset([pid5, pid6])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "Tied players should be ranked by opponent match wins.")
    print "12. Tied players should be ranked by opponent match wins."


def test_avoid_rematches():
    delete_matches_players()
    register_players(4)
    [id1, id2, id3, _] = [row[0] for row in tournament.player_standings()]
    tournament.report_match((id1, 1), (id2, 0))
    standings = tournament.player_standings()
    for (i, _, _, _, omw, _, opps) in standings:
        if id1 == i and id2 not in opps:
            raise ValueError("Opponents should be recorded.")
    pairings = tournament.swiss_pairings()
    [(pid1, _, pid2, _), (_, _, _, _)] = pairings
    if pid1 == id1 and pid2 == id2:
        raise ValueError("Players should not rematch.")
    if pid2 != id3:
        raise ValueError("When avoiding rematches, closely ranked players "
                         "should swap places")
    print "13. Rematches are avoided."


def test_multi_trnmnt_standings():
    t1 = Tournament()
    t2 = Tournament()
    if t1.tournament_id == t2.tournament_id:
        raise ValueError("New tournament instances should have a unique ID.")
    t1.register_player("Dini Petty")
    t1.register_player("Yasmeen Bleeth")
    t2.register_player("Burt Reynolds")
    t2.register_player("Ralph Nader")
    t1_names = [row[1] for row in t1.player_standings()]
    t2_names = [row[1] for row in t2.player_standings()]
    if sorted(['Yasmeen Bleeth', 'Dini Petty']) != sorted(t1_names):
        raise ValueError("T1 does not have the correct players.")
    if sorted(['Ralph Nader', 'Burt Reynolds']) != sorted(t2_names):
        raise ValueError("T2 does not have the correct players.")
    print "14. Multiple tournaments can have separate players."


def test_multi_trnmnt_pairings():
    t1 = Tournament()
    t2 = Tournament()
    for i in range(8):
        t1.register_player("player" + `i`)
    for i in range(16):
        t2.register_player("player" + `i`)
    if len(t1.swiss_pairings()) != 4:
        raise ValueError("T1 should have 4 pairings.")
    if len(t2.swiss_pairings()) != 8:
        raise ValueError("T2 should have 8 pairings.")
    print "15. Multiple tournaments have distinct standings."


def test_reuse_existing_player():
    delete_matches_players()
    tournament.register_player("Dini Petty")
    tournament.register_player("Frank Sinatra")
    t1_standings = tournament.player_standings()
    id1 = t1_standings[0][0]
    new_tournament = Tournament()
    new_tournament.register_player(id1)
    t2_standings = new_tournament.player_standings()
    if len(t2_standings) is not 1 or t2_standings[0][0] != id1:
        raise ValueError(
            "The same player from the first tournament should be reused.")
    try:
        new_tournament.register_player(999999)
    except ValueError:
        pass
    else:
        raise ValueError("Registering a player id that does not exist should "
                         "raise an error.")
    print "16. Players can be reused between tournaments."


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
    test_avoid_rematches()
    test_multi_trnmnt_standings()
    test_multi_trnmnt_pairings()
    test_reuse_existing_player()
    print "Success!  All tests pass!"
