from cocos.director import director
from cocos.scenes.transitions import SplitColsTransition, FadeTransition
from collections import defaultdict
import cocos.layer
import cocos.scene
import cocos.text
import cocos.sprite
import cocos.tiles
import cocos.actions as ac
import cocos.collision_model as cm
import cocos.euclid as eu

import pyglet.image
from pyglet.image import Animation

from actors import *
import mainmenu


class GameLayer(cocos.layer.Layer):
    
    is_event_handler = True

    def on_key_press(self, k, _):
        PlayerPlane.KEYS_PRESSED[k] = 1

    def on_key_release(self, k, _):
        PlayerPlane.KEYS_PRESSED[k] = 0

    def __init__(self, hud):
        super(GameLayer, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.hud = hud
        self.width = w
        self.height = h
        self.score = self._score = 0
        self.life = 3
        self.update_life()
        self.create_player()

        self.scrollY = 200

        #test
        self.create_Enemy()
        
        cell = 1.25 * 50
        self.collman = cm.CollisionManagerGrid(0, w, 0, h, 
                                               cell, cell)

        self.schedule(self.update)

    def update(self, dt):
        self.collman.clear()
        for _, node in self.children:
            if not isinstance(node, Explosion):
                self.collman.add(node)

        for i in range(30):
            if PlayerShoot.shoot_check[i] != 0:
                self.collide(PlayerShoot.shoot_check[i])

        PlayerPlane.Guardtime -= dt
        for other in self.collman.iter_colliding(self.player):
            if not isinstance(other, PlayerShoot):
                self.collide(self.player)
                if PlayerPlane.Guardtime < 0:
                    self.respawn_player()

        #Background move
        self.scrollY += 1
        scroller.set_focus(300, self.scrollY)
        if self.scrollY == 1150:
            self.create_Enemy()
            self.scrollY = 400

        for _, node in self.children:
            node.update(dt)

    def collide(self, node):
        if node is not None:
            for other in self.collman.iter_colliding(node):
                node.collide(other)
                return True
        return False
        
    def create_player(self):
        self.player = PlayerPlane(self.width * 0.5, 30)
        self.add(self.player)

    def respawn_player(self):
        PlayerPlane.Guardtime = 3
        self.life -= 1
        self.update_life()
        if self.life < 0:
            self.unschedule(self.update)
        else:
            self.create_player()

        
    def create_Enemy(self):
        self.add(Enemy(300,700))

    def update_life(self):
        self.hud.update_life(self.life)

    def Explose(self, position):
        self.add(Explosion(position[0],position[1]))


class HUD(cocos.layer.Layer):
    def __init__(self):
        super(HUD, self).__init__()
        w, h = director.get_window_size()
        self.score_text = self._create_text(200, 200)
        self.score_points = self._create_text(40, h-20)

    def _create_text(self, x, y):
        text = cocos.text.Label(font_size=20, font_name='Oswald',
                                anchor_x='center', anchor_y='center')
        text.position = (x, y)
        self.add(text)
        return text

    def update_score(self, score):
        self.score_text.element.text = 'Score: %s' % score

    def update_life(self, points):
        self.score_points.element.text = 'Lifes: %s' % points

        
class BackgroundLayer(cocos.layer.ScrollableLayer):
    def __init__(self):
        super().__init__()
        self.bg = cocos.sprite.Sprite("assets/rivers2.png")
        self.bg.scale = 1
        w, h = cocos.director.director.get_window_size()
        self.bg.x = 300
        self.bg.y = 750
        self.px_width = 600
        self.px_height = 1600
        self.add(self.bg)

        self.time = 0
        self.testt = 0

def new_game():
    global scroller
    hud = HUD()
    bg = BackgroundLayer()
    scroller = cocos.layer.ScrollingManager()
    scroller.add(bg, 0, 'scroll')
    
    game_layer = GameLayer(hud)
    
    return cocos.scene.Scene(scroller, game_layer, hud)
