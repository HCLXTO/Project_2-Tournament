#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#
import psycopg2#DB
import bleach#sanitization lib to prevent users attacks


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches(tournament = False):
    """Remove all the match records from the database.
    Args:
        tournament: the id of the tournament, if it is not informed it will 
            use the default tournament (id=1).
    """
    tour = tournament if tournament else 1;#1 is the default tournament
    #Interacting with the DB
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM match WHERE tour_id = %s;', (bleach.clean(tour), ))
    conn.commit()# Make the changes to the database persistent
    cursor.close()
    conn.close()


def deletePlayers(tournament = False):
    """Remove all the player records from the database.
    Args:
        tournament: the id of the tournament, if it is not informed it will 
            use the default tournament (id=1).
    """
    tour = tournament if tournament else 1;#1 is the default tournament
    #Interacting with the DB
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM player WHERE tour_id = %s;', (bleach.clean(tour), ))
    conn.commit()# Make the changes to the database persistent
    cursor.close()
    conn.close()

def countPlayers(tournament = False):
    """Returns the number of players currently registered.
    Args:
        tournament: the id of the tournament, if it is not informed it will 
            use the default tournament (id=1).
    """
    tour = tournament if tournament else 1;#1 is the default tournament
    #Interacting with the DB
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT count(*) as num FROM player WHERE tour_id = %s;',\
     (bleach.clean(tour), ))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result[0];

def registerTournament(name):
    """Adds a tournament to the tournament database.
  
    The database assigns a unique serial id number for the tournament.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the tournament's name (need not be unique).
    """
    #Interacting with the DB
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tournaments(name) VALUES (%s);', (bleach.clean(name), ))
    conn.commit()# Make the changes to the database persistent
    cursor.close()
    conn.close()

def registerPlayer(name, tournament = False):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
      tournament: the id of the tournament, if it is not informed it will 
        use the default tournament (id=1).
    """
    tour = tournament if tournament else 1;#1 is the default tournament
    #Interacting with the DB
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO player(tour_id, name) VALUES (%s,%s);', (bleach.clean(tour), bleach.clean(name)))
    conn.commit()# Make the changes to the database persistent
    cursor.close()
    conn.close()


def playerStandings(tournament = False):
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Args:
        tournament: the id of the tournament, if it is not informed it will 
            use the default tournament (id=1).

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches,OMW):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        OMW: a score based on the opponent's difficulty (omitted due to tournament_test demand)
    """
    tour = tournament if tournament else 1;#1 is the default tournament
    #Interacting with the DB
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT\
        p.id,p.name, \
        COALESCE(sum(case when m.winner=p.id then 1 else 0 end),0) as wins, \
        COALESCE (count(m.id), 0) as matches, \
        sum(case when m.winner=p.id then m.OMW else 0 end) as OMW \
        FROM player as p LEFT JOIN match as m \
        ON (p.id = m.player1 or p.id=m.player2) \
        WHERE p.tour_id = %s \
        GROUP BY p.id \
        ORDER BY wins DESC, OMW DESC;', (bleach.clean(tour), ))

    result = cursor.fetchall()
    #preparing the list to return
    p = [(row[0],bleach.clean(row[1]),row[2],row[3]) for row in result]

    cursor.close()
    conn.close()

    return p

def reportMatch(winner, loser, draw = False, tournament = False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      draw: boolean indicating if the match ended as a draw
      tournament: the id of the tournament, if it is not informed it will 
        use the default tournament (id=1).
    """
    #Set the DB connection
    conn = connect()
    cursor = conn.cursor()
    #Set the variables describing the match
    tour = tournament if tournament else 1;#1 is the default tournament
    player1 = winner
    player2 = loser
    if draw:#if it is a draw it won't have a value for winner and OMW will be 0
        winner = None
        OMW = 0
    else:#if it wasn't a draw the OMW will be the opponent's number of wins
        cursor.execute('SELECT count(*) FROM match WHERE winner = %s;'\
            ,(bleach.clean(loser), ))
        result = cursor.fetchone()
        OMW = result[0];
    
    cursor.execute('INSERT INTO match(tour_id, player1,player2, winner,OMW) \
        VALUES (%s,%s,%s,%s,%s);', (bleach.clean(tour), \
        bleach.clean(player1),bleach.clean(player2),bleach.clean(winner), \
        OMW))
    conn.commit()# Make the changes to the database persistent
    cursor.close()
    conn.close()
 
 
def swissPairings(tournament = False):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Args:
        tournament: the id of the tournament, if it is not informed it will 
            use the default tournament (id=1).

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    pairing = []
    rank = playerStandings(tournament)

    cont = 1
    for p in rank:
        if cont%2 == 0:
            pairing.append((rank[cont-2][0],rank[cont-2][1],rank[cont-1][0],\
                rank[cont-1][1]))
        cont = cont+1

    return pairing 
