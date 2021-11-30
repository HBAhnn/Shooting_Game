from cocos.director import director

import pyglet.font
import pyglet.resource

from mainmenu import new_menu


if __name__ == '__main__':
    pyglet.resource.path.append('assets')
    pyglet.resource.reindex()
    pyglet.font.add_file('assets/Oswald-Regular.ttf')
    abc = 0
    director.init(width = 600, height = 800, caption='Shooting Shooter')
    director.run(new_menu())
