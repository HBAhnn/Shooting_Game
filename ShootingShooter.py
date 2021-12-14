from cocos.director import director

import pyglet.font
import pyglet.resource

from mainmenu import new_menu
import pygame

#import cocos.audio
#import cocos.audio.pygame
#import cocos.audio.pygame.mixer

if __name__ == '__main__':
    pygame.init()
    pyglet.resource.path.append('assets')
    pyglet.resource.reindex()
    pyglet.font.add_file('assets/Oswald-Regular.ttf')
    abc = 0
    director.init(width = 600, height = 700, caption='Shooting Shooter')
    director.run(new_menu())
