import cocos.menu
import cocos.scene
import cocos.layer
import cocos.actions as ac
from cocos.director import director
from cocos.scenes.transitions import FadeTRTransition

import pyglet.app
import pygame

from gamelayer import new_game


class MainMenu(cocos.menu.Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Shooting Shooter')

        self.font_title['font_name'] = 'Oswald'
        self.font_item['font_name'] = 'Oswald'
        self.font_item_selected['font_name'] = 'Oswald'

        self.menu_anchor_y = 'center'
        self.menu_anchor_x = 'center'

        bgm = pygame.mixer.Sound(
            "C:/Users/ahn87/Desktop/dd/2Grade2/게임 프로그래밍 입문/ShootingShooter_GPI_Project/sound/bgm.mp3")
        bgm.set_volume(0.1)
        bgm.play(-1)

        items = list()
        items.append(cocos.menu.MenuItem('New Game', self.on_new_game))
        items.append(cocos.menu.ToggleMenuItem('Show FPS: ', self.show_fps, director.show_FPS))
        items.append(cocos.menu.MenuItem('Quit', pyglet.app.exit))

        self.create_menu(items, ac.ScaleTo(1.25, duration=0.25), ac.ScaleTo(1.0, duration=0.25))

    def on_new_game(self):
        director.push(FadeTRTransition(new_game(), duration=0.5))

    def show_fps(self, val):
        director.show_FPS = val


def new_menu():
    scene = cocos.scene.Scene()
    color_layer = cocos.layer.ColorLayer(150, 150, 150, 255)
    scene.add(MainMenu(), z=1)
    scene.add(color_layer, z=0)
    return scene
