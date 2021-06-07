from __future__ import absolute_import, print_function, unicode_literals
import random
import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game, check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme
from search import cooperating


# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----


# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()



def add_reservation(res, noeud, p):
	(x, y) = noeud.etat
	time = noeud.t
	if ((x, y) not in res.keys()):
		res[(x, y)] = {}
	res[(x, y)][time] = p
	res[(x, y)][time + 1] = p

def init(_boardname=None):
    global player, game
    name = _boardname if _boardname is not None else 'exAdvCoopMap'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player

def maj_reservation(res, path, p):
    for noeud in path:
        add_reservation(res, noeud, p)


def supprimer_reservation(res, path, p):
	
	for case in path:
		
		(x, y) = case.etat
		t=case.t
		
		if p == res[(x, y)][t]:
			del res[(x, y)][t]
			

		if res[(x, y)] == set():
			del res[(x, y)]


def move_player(grid2d,posPlayers,players,i, path,pos,GrilleEquipe, objectifs, score):
	
	(row, col) = path.etat
	(row_ancienne, col_ancienne) = posPlayers[i]
	
	if pos[row][col] == False:  # si ya rien dans la case j'avance
		posPlayers[i] = (row, col)
		players[i].set_rowcol(row, col)
		grid2d.init=(row, col)
		pos[row_ancienne][col_ancienne] = False
		GrilleEquipe[row_ancienne][col_ancienne] = False
		pos[row][col] = True
		GrilleEquipe[row][col] = True
		print ("pos", i, " :", row, col)
		if (row, col) == objectifs[i]:
			score[i] += 1
			print("le joueur", i, " a atteint son but!")
		return True
	return False




def main():

	# for arg in sys.argv:
	iterations = 100  # default
	if len(sys.argv) == 2:
		iterations = int(sys.argv[1])
	print ("Iterations: ")
	print (iterations)

	init()

	#-------------------------------
	# Initialisation
	#-------------------------------

	nbLignes = game.spriteBuilder.rowsize
	nbCols = game.spriteBuilder.colsize

	print("lignes", nbLignes)
	print("colonnes", nbCols)

	players = [o for o in game.layers['joueur']]
	nbPlayers = len(players)
	print("nombre de jouers ", nbPlayers)
	score = [0] * nbPlayers

	# on localise tous les états initiaux (loc du joueur)
	# positions initiales des joueurs
	initStates = [o.get_rowcol() for o in game.layers['joueur']]
	print ("Init states:", initStates)

	# on localise tous les objets ramassables
	# sur le layer ramassable
	goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
	print ("Goal states:", goalStates)

	# on localise tous les murs
	# sur le layer obstacle
	wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
	print ("Wall states:", wallStates)

	def legal_position(row, col):
		# une position legale est dans la carte et pas sur un mur
		return ((row, col) not in wallStates) and row >= 0 and row < nbLignes and col >= 0 and col < nbCols

	#-------------------------------
	# Attributaion aleatoire des fioles
	#-------------------------------

	objectifs = goalStates
	random.shuffle(objectifs)
	print("Objectif joueur 0", objectifs[0])
	print("Objectif joueur 1", objectifs[1])
	print("Objectif joueur 2", objectifs[2])
	print("Objectif joueur 3", objectifs[3])
	print("Objectif joueur 4", objectifs[4])
	print("Objectif joueur 5", objectifs[5])

	
	g = np.ones((nbLignes, nbCols), dtype=bool)
	for w in wallStates:            # putting False for walls
		g[w] = False
	path = []
	p=[]
	grillePos = np.zeros((20, 20), dtype=bool)
	posPlayers=initStates
	for (row, col) in initStates:
		grillePos[row][col] = True
	reservation={}
	reservation2={}

    
	GrilleEquipe1 = np.zeros((20, 20), dtype=bool)
	GrilleEquipe2  = np.zeros((20, 20), dtype=bool)

	pos = initStates
	bouger = np.zeros(6, dtype=bool)
	joueurs = [0, 1, 2]
	joueurs2 = [3, 4, 5]
	i=0

	for (row, col) in initStates:
		
		if (i<3):
			GrilleEquipe1[row][col] = True
		else:
			GrilleEquipe2[row][col] = True
		i+=1
		

	for iteration in range(iterations):
		if( (score[0]==1 and score[1]==1 and score[2]==1) or (score[3]==1 and score[5]==1 and score[5]==1)):
			equipe1=[0,1,2]
			equipe2=[3,4,5]
			score1 = 0
			score2 = 0 
			path_equipe1 = 0 
			path_equipe2 = 0
			for i in range(len(equipe1)) : 
				score1 += score[i]
				path_equipe1 += len(path[i])
			for i in range(len(equipe2)) :
				score2 += score[i+len(equipe1)]
				path_equipe2 += len(path[i+len(equipe1)])
			if(score1 > score2 ) :
				print("equipe1 a gagné avec un score de", score1)
				break
			if(score1 < score2 ) :
				print("equipe2 a gagné avec un score de",score2)
				break
			if(score1 == score2 ) :
				if( path_equipe1 > path_equipe2 ) :
					print("equipe1 a gagné avec un score de", score1," et un path restant de longueur", path_equipe1)
					break
				if( path_equipe1 < path_equipe2 ) :
					print("equipe2 a gagné avec un score de", score1," et un path restant de longueur", path_equipe2)
					break
				else : 
					print("égalite parfaite")
					break
           
	
		if(iteration == 0):

			for i in joueurs:
				p.append(ProblemeGrid2D(initStates[i], objectifs[i], g, 'manhattan')) #initialisation des pb pour les joueurs
		
		for joueur in joueurs: #parcours de la liste des joueurs de l'equipe 1
			
			if(bouger[joueur] == False):  # si on n est pas arrives a faire bouger l agent dans l iteration d avant ou on vient de commencer, on calcule un nouveau path
				if(iteration!=0): #Le joueur a ete bloqué par un agent de l'equipe adverse au cours de route
					
					supprimer_reservation(reservation, path[joueur],joueur) #on supprime son ancien path
					p[joueur].init=posPlayers[joueur]
					path[joueur] = cooperating.astarcooperating(p[joueur], reservation,GrilleEquipe2,iteration) #recalcul d'un autre chemin en connaissant la position des autres joueurs
                    
				else: #en debut du jeu
					path.append(cooperating.astarcooperating(p[joueur], reservation,GrilleEquipe2,iteration))
                    
				maj_reservation(reservation, path[joueur],joueur) #ajout du nouveau path dans la table de reservation
				
			bouger[joueur] = move_player( p[joueur],posPlayers, players,joueur, path[joueur][1], grillePos,GrilleEquipe1,objectifs,score) #essaie de faire bouger le joueur dans la case suivant de son path ( nouveau ou ancien)
            
			supprimer_reservation(reservation, [path[joueur][0]],joueur) #on supprime la case actuelle de reservation pour diminuer sa taille
			path[joueur]=path[joueur][1:]
			
			
			if(score[joueur]==1): # si le score du joueur a ete actualisé a 1 dans la fonction bouger joueur, on retire le joueur de la liste
				joueurs.remove(joueur)
			




        #Equipe 2
		if(iteration == 0):

			for i in joueurs2:
				p.append(ProblemeGrid2D(initStates[i], objectifs[i], g, 'manhattan'))
		
		for joueur in joueurs2: #parcours de la liste des joueurs de l'equipe 2
			print("bouger le joueur*****************",joueur)
			
			if(bouger[joueur] == False):  # si on n est pas arrives a faire bouger l agent dans l iteration d avant ou on vient de commencer, on calcule un nouveau path
				if(iteration!=0):
					
					supprimer_reservation(reservation2, path[joueur],joueur)
					p[joueur].init=posPlayers[joueur]
					path[joueur] = cooperating.astarcooperating(p[joueur], reservation2,GrilleEquipe2,iteration)
				else:
					path.append(cooperating.astarcooperating(p[joueur], reservation2,GrilleEquipe2,iteration))
                    
				maj_reservation(reservation2, path[joueur],joueur)
                
				
			bouger[joueur] = move_player( p[joueur],posPlayers, players,joueur, path[joueur][1], grillePos,GrilleEquipe2,objectifs,score)
			supprimer_reservation(reservation2, [path[joueur][0]],joueur)
			path[joueur]=path[joueur][1:]
			
			if(score[joueur]==1):
				joueurs2.remove(joueur)


            
            
        
        # on passe a l'iteration suivante du jeu
		game.mainiteration()

                
        
	pygame.quit()
    
    
    
    
    #-------------------------------
    
        
        
    
    
        
   

 
    
   

if __name__ == '__main__':
    main()
    




