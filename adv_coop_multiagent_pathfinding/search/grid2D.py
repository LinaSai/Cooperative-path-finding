# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 09:32:05 2016

@author: nicolas
"""

import numpy as np
import copy
import heapq
from abc import ABCMeta, abstractmethod
import search.probleme
from search.probleme import Probleme




def distManhattan(p1,p2):
    """ calcule la distance de Manhattan entre le tuple 
        p1 et le tuple p2
        """
    (x1,y1)=p1
    (x2,y2)=p2
    return abs(x1-x2)+abs(y1-y2) 


    
###############################################################################


class ProblemeGrid2D(Probleme): 
    """ On definit un probleme de labyrithe comme étant: 
        - un état initial
        - un état but
        - une grid, donné comme un array booléen (False: obstacle)
        - une heuristique (supporte Manhattan, euclidienne)
        """ 
    def __init__(self,init,but,grid,heuristique):
            self.init=init
            self.but=but
            self.grid=grid
            self.heuristique=heuristique
        
    
    def cost(self,e1,e2):
        """ donne le cout d'une action entre e1 et e2, 
            toujours 1 pour le taquin
            """
        return 1
        
    def estBut(self,e):
        """ retourne vrai si l'état e est un état but
            """
        return (self.but==e)
        
    def estObstacle(self,e):
        """ retorune vrai si l'état est un obsacle
            """
        return (self.grid[e]==False)
        
    def estDehors(self,etat):
        """retourne vrai si en dehors de la grille
            """
        (s,_)=self.grid.shape
        (x,y)=etat
        return ((x>=s) or (y>=s) or (x<0) or (y<0))

    
        
    def successeurs(self,etat):
            """ retourne des positions successeurs possibles
                """
            current_x,current_y = etat
            d = [(0,1),(1,0),(0,-1),(-1,0)]
            etatsApresMove = [(current_x+inc_x,current_y+inc_y) for (inc_x,inc_y) in d]
            return [e for e in etatsApresMove if not(self.estDehors(e)) and not(self.estObstacle(e))]
    
    def successeursCooperative(self,etat,grilleEnnemis,etatInitiale):
            """ retourne des positions successeurs possibles
                """
            DistancePrévision=distManhattan(etat,etatInitiale) # on calcule la distance entre l'etat initiale (ou je me trouve quand je suis entrain de calculer ce path) et l'etat actuel dans le calcul du path
            current_x,current_y = etat
            etatsApresMove=[]
            d = [(0,1),(1,0),(0,-1),(-1,0)]
            #etatsApresMove = [(current_x+inc_x,current_y+inc_y) for (inc_x,inc_y) in d]
            for (inc_x,inc_y) in d:
                if  DistancePrévision>2:# si la distance est plus grande que 2 on s'en fou si l'ennemi est la bas j'ajoute la case dans le successeur
                    etatsApresMove.append((current_x+inc_x,current_y+inc_y))
                    
                else:
                    if (grilleEnnemis[inc_x][inc_y]==False):#sinon on regarde si il n y a pas un ennemi je l'ajoute aussi
                        etatsApresMove.append((current_x+inc_x,current_y+inc_y))
                        
            return [e for e in etatsApresMove if not(self.estDehors(e)) and not(self.estObstacle(e))]

    def successeurs_slicing(self,etat,grille):
            """ retourne des positions successeurs possibles
                """
            current_x,current_y = etat
            d = [(0,1),(1,0),(0,-1),(-1,0)]
            etatsApresMove = [(current_x+inc_x,current_y+inc_y) for (inc_x,inc_y) in d]

            return [e for e in etatsApresMove if not(self.estDehors(e)) and not(self.estObstacle(e)) and (e not in grille)]

    def immatriculation(self,etat):
        """ génère une chaine permettant d'identifier un état de manière unique
            """
        s=""
        (x,y)= etat
        s+=str(x)+str(y)
        return s
        
    def h_value(self,e1,e2):
        """ applique l'heuristique pour le calcul 
            """
        if self.heuristique=='manhattan':
            h = distManhattan(e1,e2)
        elif self.heuristique=='uniform':
            h = 1
        return h


            


