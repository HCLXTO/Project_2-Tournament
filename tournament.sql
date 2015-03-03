--Create Database statement for the tournament project.
CREATE DATABASE tournament; 
-- Table definitions for the tournament project.

--table that stores the tournament info
CREATE TABLE tournaments ( id SERIAL PRIMARY KEY,
						name TEXT NOT NULL);

--table that stores the player info
CREATE TABLE player ( id SERIAL PRIMARY KEY,
						tour_id INT references tournaments(id) NOT NULL,
						name TEXT NOT NULL);

--table that stores the match info, main contraints are:
--every match must have tour_id,players 1 and 2
--the players must be diferent, and
--the combination of tour_id, players must be unique
--preventing to have the result of the same match inputed twice
CREATE TABLE match ( id SERIAL PRIMARY KEY,
						tour_id INT references tournaments(id) NOT NULL,
						player1 INT references player(id) NOT NULL,
						player2 INT references player(id) NOT NULL,
						winner INT references player(id),
						OMW INT,
						CONSTRAINT dif_players CHECK (player1 != player2),
						CONSTRAINT unique_match UNIQUE (tour_id, player1, player2));
