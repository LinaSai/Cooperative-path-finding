# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme




# ---- ---- ---- ---- ---- ----
# ---- Misc                ----
# ---- ---- ---- ---- ---- ----




# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
	global player,game
	name = _boardname if _boardname is not None else 'exAdvCoopMap'
	game = Game('Cartes/' + name + '.json', SpriteBuilder)
	game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
	game.populate_sprite_names(game.O)
	game.fps = 5  # frames per second
	game.mainiteration()
	player = game.player
    
 

	  
def main():

	#for arg in sys.argv:
	iterations = 100 # default
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
	print("nombre de jouers ",nbPlayers)
	score = [0]*nbPlayers
    
       
           
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
    
	def legal_position(row,col):
		# une position legale est dans la carte et pas sur un mur
		return ((row,col) not in wallStates) and row>=0 and row<nbLignes and col>=0 and col<nbCols
        
    #-------------------------------
    # Attributaion aleatoire des fioles 
    #-------------------------------
	
	objectifs=goalStates
	random.shuffle(objectifs)
	print("Objectif joueur 0", objectifs[0])
	print("Objectif joueur 1", objectifs[1])
	print("Objectif joueur 2", objectifs[2])
	print("Objectif joueur 3", objectifs[3])
	print("Objectif joueur 4", objectifs[4])
	print("Objectif joueur 5", objectifs[5])

	#-------------------------------
	# Carte demo 
	# 2 joueurs 
	# Joueur 0: A*
	# Joueur 1: random walker
	#-------------------------------

	#-------------------------------
	# calcul A* pour le joueur 1
	#-------------------------------



	g =np.ones((nbLignes,nbCols),dtype=bool)  # par defaut la matrice comprend des True  
	for w in wallStates:            # putting False for walls
		g[w]=False

	equipe1=[0,1,2]
	equipe2=[3,4,5]
	posPlayers=initStates
	path=[]
	prob=[]
	score=[0,0,0,0,0,0]

	#-------------------------------
	# Boucle principale de déplacements 
	#-------------------------------

		    


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


		for joueur1 in equipe1:
			if(iteration == 0):	
				prob.append(ProblemeGrid2D(initStates[joueur1], objectifs[joueur1], g, 'manhattan')) #creation des pb pour chaque joueur
				path.append(probleme.astar(prob[joueur1])) # calcul du path initial

            
			else:
				print()
				if (score[joueur1]==0):
					
					print("longueur pqth",joueur1,len(path[joueur1]))
					row,col = path[joueur1][iteration] #prochaine case où je veux me déplacer
					if (row,col) == objectifs[joueur1]:
							print("Score",joueur1,"score",score[joueur1])
							score[joueur1] += 1
							posPlayers[joueur1] = (row,col)
							players[joueur1].set_rowcol(row,col)
							break	
					if (row,col) in posPlayers: #prochaine case est occupée => COLLISION !!
						prob[joueur1].init = path[joueur1][iteration-1] #je change la position initiale dans le problemeGrid2D du joueur et je rappele le A*
						if( len(path[joueur1]) >= iteration+2 ):
							#print("Collision",(row,col) )
							#print("PATH",path[joueur])
							path_tmp=path[joueur1][iteration+1:] 
							
							prob[joueur1].but= path[joueur1][iteration+1]
							chemin=probleme.astar_path_slicing(prob[joueur1],posPlayers)
							path[joueur1] = path[joueur1][0:iteration-1]+chemin+ path_tmp
						
                        
						else:
							path_restant= path[joueur1][iteration-1:]
							path[joueur1]=path[joueur1][0:iteration-1]+[posPlayers[joueur1]] + path_restant  #il attend sìl n a pas trouve de chemin
							# print("Je ne bouge pas joueur ",joueur1) 
							# print("Je ne bouge pas joueur ",path[joueur1])
					 
					row,col = path[joueur1][iteration]
					if (row,col)  not in posPlayers:
						posPlayers[joueur1] = (row,col)
						players[joueur1].set_rowcol(row,col)
					else : #si la case prohcaine est occupée
						path_restant= path[joueur1][iteration-1:]
						path[joueur1]=path[joueur1][0:iteration-1]+[posPlayers[joueur1]] + path_restant  
						r,c=posPlayers[joueur1] 
						players[joueur1].set_rowcol(r,c)

						

				else:
					continue


		for joueur2 in equipe2:
			if(iteration == 0):	
				prob.append(ProblemeGrid2D(initStates[joueur2], objectifs[joueur2], g, 'manhattan')) #creation des pb pour chaque joueur
				path.append(probleme.astar(prob[joueur2])) # calcul du path initial

            
			else:
				print()
				if (score[joueur2]==0):
					
					print("longueur pqth",joueur2,len(path[joueur2]))
					row,col = path[joueur2][iteration] #prochaine case où je veux me déplacer
					if (row,col) == objectifs[joueur2]:
							print("Score",joueur2,"score",score[joueur2])
							score[joueur2] += 1
							posPlayers[joueur2] = (row,col)
							players[joueur2].set_rowcol(row,col)
							continue

					if (row,col) in posPlayers: #prochaine case est occupée => COLLISION !!
						prob[joueur2].init = path[joueur2][iteration-1] #je change la position initiale dans le problemeGrid2D du joueur et je rappele le A*
						if( len(path[joueur2]) >= iteration+2 ):
							#print("Collision",(row,col) )
							#print("PATH",path[joueur])
							path_tmp=path[joueur2][iteration+1:] 
							
							prob[joueur2].but= path[joueur2][iteration+1]
							chemin=probleme.astar_path_slicing(prob[joueur2],posPlayers)
							path[joueur2] = path[joueur2][0:iteration-1]+chemin+ path_tmp
						
                        
						else:
							path_restant= path[joueur2][iteration-1:]
							path[joueur2]=path[joueur2][0:iteration-1]+[posPlayers[joueur2]] + path_restant  #il attend sìl n a pas trouve de chemin
							# print("Je ne bouge pas joueur ",joueur2) 
							# print("Je ne bouge pas joueur ",path[joueur2])
					 
					row,col = path[joueur2][iteration]
					if (row,col)  not in posPlayers:
						posPlayers[joueur2] = (row,col)
						players[joueur2].set_rowcol(row,col)
					else : #si la case prohcaine est occupée
						path_restant= path[joueur2][iteration-1:]
						path[joueur2]=path[joueur2][0:iteration-1]+[posPlayers[joueur2]] + path_restant  
						r,c=posPlayers[joueur2] 
						players[joueur2].set_rowcol(r,c)

							

				else:
					continue		
			
       
        
        
        
       
        
        
            
        
        # on passe a l'iteration suivante du jeu
		game.mainiteration()

                
        
            
    
	print ("scores:", score)
	pygame.quit()
    
    
    
    
    #-------------------------------
    
        
        
    
    
        
   

 
    
   

if __name__ == '__main__':
    main()
    


