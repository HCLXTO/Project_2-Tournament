Hello, this application was built by Henrique Calixto in order to attend to the second project
of the Full Stack Web Developer course at Udacity.com

The project's objective is to make a database schema to store the game matches between players
in a Swiss-system tournament

 The project is composed by the following files:
 	1)tournament.sql: this file is the database declaration file, all the SQL to create the
 	database are declared in this file.
 	2)tournament.py: this module is composed of python functions that interact with the database
 	and enable the swiss-sistem tournament rules.
 	3)tournament_test.py: this file is a set of test cases to determine if the database schema
 	is working properly.

 To run this application:
 	1)Install Vagrant (https://www.vagrantup.com/) and VirtualBox (https://www.virtualbox.org/)
 	2)Clone the fullstack-nanodegree-vm repository (https://github.com/udacity/fullstack-nanodegree-vm)
 	3)Replace the content of the tournament folder (fullstack\vagrant\tournament) with this application's content
 	4)Launch the Vagrant VM
 	5)In the VM run the command 'psql' to go to the psql terminal and then hit '\i tournament.sql' to
 		create the tournament database (based on the schema defined in tournament.sql file) into your machine
 	6)Now you are ready to run the functions in the torunament.py file to make your own tournaments, just
 		import the torunament.py in your script and you have access to all it's functions.