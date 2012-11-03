import pygame
from pygame.locals import *

__version__ = "0.1"

"""
    SceneCreator 
    
    SceneCreator fait partie de la suite logicielle FreeGameTools, il sert
    au prototypage rapide de scènes à partir d'un ensemble de sprites.
    
    Le programme se base sur le format JSON pour charger et sauver l'ensemble
    des scènes.
    
    SceneCreator is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    Copyright 2012, Léo Germond
"""

class Scene:
    file_data = {
        "resolution" : (800,600),
        "scale" : 1, 
        "objects" : [],
        "background" : "black"
    }
    
    def __init__(self, sprites_dir = ".", scene_file = None):
        import json
        print("Launching with sprite dir {0} and scene file {1}".format(sprites_dir, scene_file))
        self.sprites_dir = sprites_dir
        if scene_file == None:
            self.scene = {}
        else:
            self.scene_file = scene_file
            f = open(self.scene_file, "r")
            self.scene = json.load(f)
            print("{0} scene loaded with {1} objects".format(self.resolution, len(self.objects)))
        
    def displayOn(self, surface):
        surface.fill(pygame.Color(self.background), pygame.Rect((0,0),  self.resolution))
        for sprite_name, position in self.objects:
            sprite = self.getImage(sprite_name)
            surface.blit(sprite, position)

    def getImage(self, sprite_name):
        import os
        image =  pygame.image.load(os.path.join(self.sprites_dir, sprite_name)).convert_alpha()
        if self.scale > 1:
            image = pygame.transform.scale(image, (self.scale * image.get_width(), self.scale * image.get_height()))
        return image
    
    def listAllImages(self):
        import os
        import glob
        return map(os.path.basename, glob.glob(os.path.join(self.sprites_dir, "*.[pP][nN][gG]")))
        
    def objectAt(self, pos):
        from pygame import Rect
        for (rn, (s, p)) in enumerate(self.objects[::-1]):
            img = self.getImage(s)
            n = len(self.objects) - 1 - rn
            if Rect(p, img.get_size()).collidepoint(pos) and img.get_at(self.distToObject(n, pos)).a > 0:
                print("Found sprite {0}: {1}".format(n, self.objects[n][0]))
                return n
        return None
    
    def distToObject(self, object, pos):
        xo, yo = self.objects[object][1]
        return pos[0] - xo, pos[1] - yo
        
    def moveObject(self, object, to):
        self.objects[object][1] = to
    
    def deleteObject(self, object):
        del self.objects[object]
    
    def copyObject(self, n):
        import copy
        newobject = copy.deepcopy(self.objects[n])
        self.objects.insert(n + 1, newobject)
        return n + 1
    
    def putToBackground(self, n):
        ob = self.objects[n]
        del self.objects[n]
        self.objects.insert(0, ob)
        return 0
        
    def putToForeground(self, n):
        ob = self.objects[n]
        del self.objects[n]
        self.objects.append(ob)
        return len(self.objects) - 1
    
    def changeToNextImage(self, n):
        ob = self.objects[n]
        imgs = list(self.listAllImages())
        cur_img = imgs.index(ob[0])
        ob[0] = imgs[(cur_img + 1)%len(imgs)]        
        
    def changeToPreviousImage(self, n):
        ob = self.objects[n]
        imgs = list(self.listAllImages())
        cur_img = imgs.index(ob[0])
        ob[0] = imgs[(cur_img - 1)%len(imgs)]
    
    def saveToFile(self):
        import json
        f = open(self.scene_file, "w")
        # Indent = 0 => "pretty" print (newlines)
        json.dump(self.scene, f, indent=0)
        print("Scene saved to {0}".format(self.scene_file)) 
    
    def __getattr__(self, name):
        if name in Scene.file_data.keys():
            default = Scene.file_data[name]
            return self.scene.get(name, default)
        else:
            return self.__dict__[name]
        
    def __setattr__(self, name, value):
        if name in Scene.file_data.keys():
            self.scene[name] = value
        else:
            self.__dict__[name] = value
        
class SceneCreator:
    def __init__(self, scene):
        """
            Lance l'application SceneCreator sur la scène donnée
        """
        self.scene = scene
        self.screen = pygame.display.set_mode(scene.resolution, pygame.RESIZABLE)
        self.clock_fps = pygame.time.Clock()
        
        self.selected_sprite = None
        self.delta_selected = [0, 0]
        
        self.quit = False
        while not self.quit:
            self.events()
            self.refresh()
    
    def refresh(self):
        self.scene.displayOn(self.screen)
        pygame.display.flip()
        self.clock_fps.tick(60)
        pygame.display.set_caption("SceneCreator v{0}   {1} FPS".format(
            __version__, self.clock_fps.get_fps()))

    def events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit = True
            elif event.type == VIDEORESIZE:
                self.scene.resolution = event.size
                pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    if not self.selected_sprite is None:
                        print("Sprite {0} deselected".format(self.selected_sprite))
                        self.selected_sprite = None
                    else:
                        self.selected_sprite = self.scene.objectAt(event.pos)
                        if not self.selected_sprite is None:                 
                            self.delta_selected = self.scene.distToObject(self.selected_sprite, event.pos)
                            print("Sprite {0} selected".format(self.selected_sprite))
                elif event.button == 3:
                    if not self.selected_sprite is None:
                        self.scene.deleteObject(self.selected_sprite)
                        self.selected_sprite = None
            elif event.type == KEYDOWN:
                if event.key == K_c:
                    if not self.selected_sprite is None:
                        self.selected_sprite = self.scene.copyObject(self.selected_sprite)
                elif event.key == K_f:
                    if not self.selected_sprite is None:
                        self.selected_sprite = self.scene.putToForeground(self.selected_sprite)
                elif event.key == K_b:
                    if not self.selected_sprite is None:
                        self.selected_sprite = self.scene.putToBackground(self.selected_sprite)
                elif event.key == K_p:
                    if not self.selected_sprite is None:
                        self.scene.changeToNextImage(self.selected_sprite)
                elif event.key == K_o:
                    if not self.selected_sprite is None:
                        self.scene.changeToPreviousImage(self.selected_sprite)
                elif event.key == K_s:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.scene.saveToFile()
                elif event.key == K_PAGEDOWN:
                    if self.scene.scale > 1:
                        self.scene.scale -= 1
                elif event.key == K_PAGEUP:
                    self.scene.scale += 1
                elif event.key == K_RIGHT:
                    pos = pygame.mouse.get_pos()
                    move = self.scene.scale
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                         move *= 10
                    pygame.mouse.set_pos((pos[0] + move, pos[1]))
                elif event.key == K_LEFT:
                    pos = pygame.mouse.get_pos()
                    move = self.scene.scale
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                         move *= 10
                    pygame.mouse.set_pos((pos[0] - move, pos[1]))
                elif event.key == K_UP:
                    pos = pygame.mouse.get_pos()
                    move = self.scene.scale
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                         move *= 10
                    pygame.mouse.set_pos((pos[0], pos[1] - move))
                elif event.key == K_DOWN:
                    pos = pygame.mouse.get_pos()
                    move = self.scene.scale
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                         move *= 10
                    pygame.mouse.set_pos((pos[0], pos[1] + move))
        
        if not self.selected_sprite is None:
            new_pos_x = pygame.mouse.get_pos()[0] - self.delta_selected[0]
            new_pos_y = pygame.mouse.get_pos()[1] - self.delta_selected[1]
            self.scene.moveObject(self.selected_sprite, (new_pos_x, new_pos_y))
                    
if __name__ == "__main__":
    import sys
    pygame.init()
    if len(sys.argv) > 1:
        scene = Scene(*sys.argv[1:])
    else:
        scene = Scene()
    
    SceneCreator(scene)