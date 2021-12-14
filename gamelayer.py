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
from cocos.scenes.transitions import FadeTRTransition
import pygame
#import cocos.audio
#import cocos.audio.pygame
#import cocos.audio.pygame.mixer

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
        self.stage_level = 1
        self.create_player()
        self.gameoverbool = 0

        self.missile = 2

        self.life1 = Life_image(20, 680)
        self.add(self.life1)
        self.life2 = Life_image(60, 680)
        self.add(self.life2)
        self.life3 = Life_image(100, 680)
        self.add(self.life3)

        self.missile1 = Missile_image(20, 640)
        self.add(self.missile1)
        self.missile2 = Missile_image(60, 640)
        self.add(self.missile2)

        self.delay = 0
        self.missile_delay = 0

        self.stage_y_end = 1150
        self.stage_y_start = 400

        self.scrollY = 200

        self.add(Boss(300, 800))
        self.stage_text = 0

        #test
        self.create_Enemy()
        self.create_delay = 3
        
        cell = 50
        self.collman = cm.CollisionManagerGrid(0, w, 0, h, 
                                               cell, cell)

        self.schedule(self.update)

    def update(self, dt):
        self.collman.clear()
        for _, node in self.children:
            if not isinstance(node, Explosion) and not isinstance(node, Life_image) and not isinstance(node, Bomb_Explosion) and not isinstance(node, Missile_image) and not isinstance(node, Missile):
                self.collman.add(node)

        #플레이어 총알 콜리전 체크
        if self.stage_level == 1:
            for i in range(15):
                if PlayerShoot.shoot_check[i] != 0:
                    self.collide(PlayerShoot.shoot_check[i])
        else:
            for i in range(15):
                if PlayerShoot2.shoot_check[i] != 0:
                    self.collide(PlayerShoot2.shoot_check[i])
                
        #player 무적 시간
        PlayerPlane.Guardtime -= dt
        for other in self.collman.iter_colliding(self.player):
            if not isinstance(other, PlayerShoot) and not isinstance(other, PlayerShoot2):
                self.collide(self.player)
                if PlayerPlane.Guardtime < 0:
                    self.respawn_player()


        #미사일 발사
        self.missile_delay -= dt
        if PlayerPlane.KEYS_PRESSED[key.Z] == 1 and self.missile > 0 and self.missile_delay < 0:
            if self.missile == 2:
                self.missile2.kill()
            elif self.missile == 1:
                self.missile1.kill()
            self.missile_delay = 3
            self.missile -= 1
            self.add(Missile(300, 0))

        #레벨업 메세지 제거
        self.stage_text -= dt
        if self.stage_text > 0 and self.stage_text < 3:
            self.stage_text = 0
            self.delete_stage()

        #적군 생성
        self.delay += dt
        if self.delay > self.create_delay:
            self.delay = 0
            self.create_Enemy()

        #Background move
        self.scrollY += 1
        scroller.set_focus(300, self.scrollY)
        if self.scrollY == self.stage_y_end:
            self.scrollY = self.stage_y_start
        for _, node in self.children:
            node.update(dt)

        #restart
        if self.gameoverbool == 1:
            if PlayerPlane.KEYS_PRESSED[key.R] == 1:
                director.push(FadeTRTransition(new_game(), duration=0.5))

    def collide(self, node):
        if node is not None:
            for other in self.collman.iter_colliding(node):
                node.collide(other)
                return True
        return False
        
    def create_player(self):
        self.player = PlayerPlane(self.width * 0.5, 30)
        self.add(self.player)
        if self.stage_level == 2:
            self.player.plane_level = 2

    def respawn_player(self):
        PlayerPlane.Guardtime = 3
        if self.life == 3:
            self.life3.kill()
        elif self.life == 2:
            self.life2.kill()
        elif self.life == 1:
            self.life1.kill()
        self.life -= 1
        if self.life < 0:
            self.hud.show_game_over()
            self.gameoverbool = 1
        else:
            self.update_life()
            self.create_player()

        
    def create_Enemy(self):
        self.add(Enemy(300,700))

    def update_life(self):
        self.hud.update_life(self.life)

    def level_up(self):
        self.stage_level = 2
        self.player.plane_level = 2
        self.player.shootcount = 0
        for i in range(15):
            PlayerShoot.shoot_check[i] = 0
        self.stage_y_end = 2650
        self.stage_y_start = 1900 #1150 400
        self.create_delay = 1.5
        self.do(ac.Delay(3) + ac.CallFunc(self.create_boss2))
        self.showstage()
        self.stage_text = 5

    def showstage(self):
        self.hud.show_stage()

    def delete_stage(self):
        self.hud.delete_stage()

    def create_boss2(self):
        self.add(Boss2(300, 900))

    def bomb_boom(self):
        self.add(Bomb_Explosion(300,400))
        for _, node in self.children:
            if isinstance(node, Enemy):
                node.hit(10)
            if isinstance(node, Boss) or isinstance(node, Boss2):
                node.hit(10)



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

    def show_stage(self):
        w, h = cocos.director.director.get_window_size()
        self.stage2 = cocos.text.Label('Stage 2', font_size=50, color = (255,255,0,255),
                                     anchor_x='center',
                                     anchor_y='center')
        self.stage2.position = w * 0.5, h * 0.5
        self.add(self.stage2)

    def delete_stage(self):
        self.stage2.kill()

    def show_game_over(self):
        w, h = cocos.director.director.get_window_size()
        game_over = cocos.text.Label('Game Over', font_size=70, bold = 1, color = (255,100,100,255),
                                     anchor_x='center',
                                     anchor_y='center')
        game_over.position = w * 0.5, h * 0.5
        restart = cocos.text.Label('Press R to restart', font_size=50, color = (255,255,255,255),
                                     anchor_x='center',
                                     anchor_y='center')
        restart.position = w * 0.5, h * 0.4
        self.add(game_over)
        self.add(restart)
        
class BackgroundLayer(cocos.layer.ScrollableLayer):
    def __init__(self):
        super().__init__()
        self.bg = cocos.sprite.Sprite("assets/river3.jpg")
        self.bg.scale = 1
        w, h = cocos.director.director.get_window_size()
        self.bg.x = 300
        self.bg.y = 1500
        self.px_width = 600
        self.px_height = 3200
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
