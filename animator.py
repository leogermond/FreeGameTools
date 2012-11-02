﻿import pygame
from pygame.locals import *
from pygame import Color

# La version du logicel
__version__ = "0.1"

# La résolution du programme
RESOLUTION = (400,300)

class Animator:
    """ La classe Animator représente le programme "Animator" """
    def __init__(self, resolution, images_path):
        """ 
            Lancé quand un objet de la classe Animator est créé (c'est à dire 
            qu'on lance le programme) 
        """
        # Créée un objet "Clock" pour pouvoir afficher à 60 images/sec
        self.clock_fps = pygame.time.Clock()
        # Vitesse d'affichage: 0 = 60 images/secondes, 1 = 30 images/secondes, 2 = 15 images par secondes
        # Attention: plus c'est haut plus c'est lent !
        self.speed = 4
        # Compteur pour garder la trace de ou on est dans l'animation
        self.anim_count = 0
        # Par défaut on garde la taille de l'image
        self.scale = 1
        # Frames de l'animation, triées par ordre alphabétique
        self.images = []
        # Dossier ou sont stockées les images
        self.images_path = images_path
        # Créée la zone d'affichage et la conserve en mémoire pour dessiner dessus plus tard
        self.screen = pygame.display.set_mode(resolution)
        # On affiche les paramètres du programme
        self.displayParameters()

        # On boucle tant qu'on n'a pas quitté
        self.quit = False
        while not self.quit:
            # On traite chaque évènement (event) qui se produit
            for event in pygame.event.get():
                if event.type == QUIT: # L'évènement est de quitter
                    self.quit = True
                    break # On ne traite pas d'évènements supplémentaires
                elif event.type == KEYDOWN: # L'évènement est "touche appuyée"
                    # Suivant la touche appuyée, on fait un traitement différent
                    if event.key == K_q: # A pressé (QWERTY)
                        self.speed -= 1 # Augmente la vitesse de défilement
                        if self.speed < 0: # On ne peut pas descendre en dessous de 0
                            self.speed = 0 
                    elif event.key == K_w: # Z pressé (QWERTY)
                        self.speed += 1 # Augmente la vitesse de défilement
                    elif event.key == K_e: # ...
                        # Réduit la taille de l'image
                        self.scale -= 1
                        if self.scale < 1: # On ne peut pas descendre en dessous de 1
                            self.scale = 1 
                        else: # L'image a réduit de taille
                            # On remplit de noir les zones de l'écran ou il y avait l'ancienne image
                            self.screen.fill(Color("black"))
                    elif event.key == K_r:
                        # Agrandit la taille de l'image
                        self.scale += 1
                    elif event.key == K_t:
                        pass # Rien
            # On rafraichit l'affichage
            self.refresh()
        # On a quitté
        print("Fin du programme !")
    
    def displayParameters(self):
        """ Affiche les paramètres du programme en haut de la fenetre """
        pygame.display.set_caption("Animator v{0}: {1}    Speed {2}    {3} FPS".format(
            __version__, self.images_path, self.speed, self.clock_fps.get_fps()))
    
    def refresh(self):
        """ Rafraichit l'affichage = Redessine l'image """
        FPS = 60 # 60 images par secondes
        self.reload_files() # Recharge les fichiers si ils ont changés 
        self.anim_count += 1 # Incrémente le compteur                                          
        # On récupère l'image à afficher
        # Le calcul utilise l'opérateur modulo: '%' et la taille du tableau images (= nombre de frames): 'len(self.images)'
        if(len(self.images) > 0): # Il faut qu'il y ait au moins une image à afficher !
            frame = self.images[int(self.anim_count/(self.speed + 1)) % len(self.images)]
            # On dessine l'image
            self.screen.blit(frame, (0,0)) # On dessine l'image
        else: # Il n'y a aucune image a afficher :(
            self.screen.fill(Color("gray")) # On remplit l'écran de gris
        
        pygame.display.flip() # Obligatoire pour prendre en compte les changements d'affichage
            
        self.clock_fps.tick(FPS) # Attend quelques temps pour être sur de ne pas afficher plus vite que 60 FPS
        self.displayParameters() # On affiche les parametres
    
    def reload_files(self):
        """ Lit le dossier et recharge les images qui ont changé """
        from glob import glob # On importe la fonction 'glob' depuis le module 'glob'
        self.images = [] # On vide les images
        for filename in glob("{0}/*.[pP][nN][gG]".format(self.images_path)):
            # Pour chaque image trouvée dans le dossier 
            try: # Utilisé pour gérer les erreurs (appellées "exceptions")
                image = pygame.image.load(filename).convert() # On la charge depuis le disque
                if self.scale > 1: # On redimensionne l'image
                    # On redimensionne en gardant les proportions de l'image
                    width = image.get_width() * self.scale
                    height = image.get_height() * self.scale
                    image = pygame.transform.scale(image, (width, height))
                    
                self.images.append(image) # On l'ajoute à la liste des images
            except: # Au cas ou une erreur à eu lieue depuis le try, on se retrouve la
                pass # On ignore l'erreur (par exemple: image illisible ...)
                
def getImagesPath():
    """ Détermine le chemin demandé par l'utilisateur """
    # Si un argument a été donné en lançant le programme: c'est le chemin
    import sys
    if len(sys.argv) > 1: # Il y a 1 argument ou plus
        return sys.argv[1] # On retourne l'argument numéro 1 (le numéro 0 est le nom et le chemin du programme)
    else: # Sinon on demande à l'utilisateur de donner le chemin à la main dans la console
        return input("Dossier: ")
        
def main():
    """ Initialise pygame et lance un programme Animator """
    
    # Initialise pygame (obligatoire de le faire au début)
    pygame.init()
    # On récupère le dossier ou sont stockées les images
    path = getImagesPath()
    # On lance un programme Animator en 800x600
    Animator(RESOLUTION, path)

if __name__ == "__main__":
    """ Ce code est exécuté quand ce fichier python est lancé directement (double click, 
    par exemple) """
    # On initialise pygame et on lance l'application ...
    main()