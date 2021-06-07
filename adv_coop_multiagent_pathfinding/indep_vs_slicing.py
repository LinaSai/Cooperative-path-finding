# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain


import pygame
import time

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
		
		print("ITERATION------------------------------",iteration)
		if( (score[0]+score[1]+score[2]==3) or (score[3]+score[4]+score[5]==3)):	
			print("GAME OVER")
			if (score[0]+score[1]+score[2]==score[3]+score[4]+score[5]):
				if (len(path[1])+len(path[0])+len(path[2]))==(len(path[3])+len(path[4])+len(path[5])):
					print("EGALITÉ")
				else:
					if (len(path[1])+len(path[0])+len(path[2]))>(len(path[3])+len(path[4])+len(path[5])):
						print("L'EQUIPE 1 A GAGNÉ")
					else:
						print("L'EQUIPE 2 A GAGNÉ")
			else:
				if (score[0]+score[1]+score[2]>score[3]+score[4]+score[5]):
					print("L'EQUIPE 1 A GAGNÉ")
				else:
					print("L'EQUIPE 2 A GAGNÉ")		
				break


		for joueur1 in equipe1:
			if(iteration == 0):
				prob.append(ProblemeGrid2D(initStates[joueur1], objectifs[joueur1], g, 'manhattan')) #creation des pb pour chaque joueur
				path.append(probleme.astar(prob[joueur1])) # calcul du path initial

			
			else:
				print()
				if (score[joueur1]==0):
					print("longueur path",joueur1,len(path[joueur1]))
					print("path",path[joueur1])
					row,col = path[joueur1][iteration] #prochaine case où je veux me déplacer

					if (row,col) == objectifs[joueur1]:
							print("Score",joueur1,"score",score[joueur1])
							players[joueur1].set_rowcol(row,col)
							posPlayers[joueur1] = (row,col)
							score[joueur1] += 1
							continue

					if (row,col) in posPlayers: #prochaine case est occupée => COLLISION !!
						
						prob[joueur1].init = path[joueur1][iteration-1] #Pour recalculer le path, la case initiale est ma case actuelle
						x,y=path[joueur1][iteration-1]
						grille=np.copy(g) # g est la grille contenant les WallStates
						grille[row][col]=False #consideter la case prise comme un mur

						a = ProblemeGrid2D(prob[joueur1].init, objectifs[joueur1], grille, 'manhattan')
						newPath = probleme.astar(a) #Le nouveau path calculé ne passera pas par la case (row,col) car il la considere comme un mur
						
						
						if ( newPath[-1] != objectifs[joueur1] ): #si la derniere case du nouveau path calculé n'est pas mon objectif, le joueur reste immobile
							path_restant= path[joueur1][iteration:]
							path[joueur1]=path[joueur1][0:iteration-1]+[posPlayers[joueur1]] + path_restant  #il attend sìl n a pas trouve de chemin
							print("Je ne bouge pas joueur ",joueur1)
							print("Je ne bouge pas joueur ",path[joueur1])

						else: # le nouveau path est valide
							print("Nouveau path trouve ",joueur1)
							path[joueur1] = path[joueur1][0:iteration-1]+newPath
							print("Nouveau path trouve ",path[joueur1])

					
					row,col = path[joueur1][iteration]
					if (row,col)  not in posPlayers:
						posPlayers[joueur1] = (row,col)
						players[joueur1].set_rowcol(row,col)
					else : #si la case prohcaine est occupée
						print("Il y a quelqu un dans le nouveau")
						path_restant= path[joueur1][iteration:]
						path[joueur1]=path[joueur1][0:iteration-1]+[posPlayers[joueur1]] + path_restant
						r,c=posPlayers[joueur1]
						players[joueur1].set_rowcol(r,c)
						print("Path",path[joueur1])
				else :
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
						
							path_tmp=path[joueur2][iteration+1:]
							
							prob[joueur2].but= path[joueur2][iteration+1]
							chemin=probleme.astar_path_slicing(prob[joueur2],posPlayers)
							path[joueur2] = path[joueur2][0:iteration-1]+chemin+ path_tmp
						
						
						else:
							path_restant= path[joueur2][iteration-1:]
							path[joueur2]=path[joueur2][0:iteration-1]+[posPlayers[joueur2]] + path_restant  #il attend sìl n a pas trouve de chemin
							
					
					row,col = path[joueur2][iteration]
					if (row,col)  not in posPlayers:
						posPlayers[joueur2] = (row,col)
						players[joueur2].set_rowcol(row,col)
					else : #si la case prohcaine est occupée
						path_restant= path[joueur2][iteration-1:]
						path[joueur2]=path[joueur2][0:iteration-1]+[posPlayers[joueur2]] + path_restant
						r,c=posPlayers[joueur2]
						players[joueur2].set_rowcol(r,c)
				else :
					continue
		#time.sleep(1)	
		
        
		# stepwise=True
		# if stepwise :
		# 	stop_stepwise = input("Press Enter to continue (s to stop)...")
		# 	if stop_stepwise=="s":
		# 		stepwise=False 
       
        
        
            
        
        # on passe a l'iteration suivante du jeu
		game.mainiteration()

                
        
            
    
	#print ("scores:", score)
	pygame.quit()
    
    
    
    
    #-------------------------------
    
        
        
    
    
        
   

 
    
   

if __name__ == '__main__':
    main()
    


