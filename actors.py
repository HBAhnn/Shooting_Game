from cocos.director import director
from cocos.scenes.transitions import SplitColsTransition, FadeTransition
from collections import defaultdict
from pyglet.image import load, ImageGrid, Animation
from pyglet.window import key

import cocos.audio
import cocos.sprite
import cocos.actions as ac
import cocos.collision_model as cm
import cocos.euclid as eu

import pyglet.image
from pyglet.image import Animation



class Actor(cocos.sprite.Sprite):
    def __init__(self, image, x, y):
        super(Actor, self).__init__(image)
        self.position = eu.Vector2(x, y)
        self._cshape = cm.CircleShape(self.position,
                                      self.width * 0.5)

    def move(self, offset):
        self.position += offset
        
    @property
    def cshape(self):
        self._cshape.center = eu.Vector2(self.x, self.y)
        return self._cshape
    
    def update(self, elapsed):
        pass

    def collide(self, other):
        pass


class PlayerPlane(Actor):
    KEYS_PRESSED = defaultdict(int)
    def __init__(self, x, y):
        super(PlayerPlane, self).__init__('assets/Player_Character.png', x, y)
        self.scale = 0.1
        self.Xspeed = eu.Vector2(200, 0)
        self.Yspeed = eu.Vector2(0, 200)
        self.elapsed = 0
        self.do(ac.Blink(6,3))
        self.cshape.r *= 0.1
        
        #width = height = 51

    def update(self, elapsed):
        pressed = PlayerPlane.KEYS_PRESSED
        space_pressed = pressed[key.SPACE] == 1


        self.elapsed -= elapsed
        if self.elapsed < 0.1 and space_pressed:
            self.elapsed = 0.3
            for i in range(15):
                if PlayerShoot.shoot_check[i] == 0:
                    PlayerShoot.shoot_check[i] = PlayerShoot(self.x, self.y + 40, i)
                    self.parent.add(PlayerShoot.shoot_check[i])
                    break
        
        Xmovement = pressed[key.RIGHT] - pressed[key.LEFT]
        Ymovement = pressed[key.UP] - pressed[key.DOWN]
        w = self.width * 0.5
        self.move(self.Xspeed * Xmovement * elapsed, self.Yspeed * Ymovement * elapsed)

    def move(self, Xmove, Ymove):
        self.position += Xmove
        self.position += Ymove

class Shoot(Actor):
    def __init__(self, x, y, img='assets/One_shot.png'):
        super(Shoot, self).__init__(img, x, y)
        self.speed = eu.Vector2(0, -400)

    def update(self, elapsed):
        self.move(self.speed * elapsed)

class PlayerShoot(Shoot):
    shoot_check = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def __init__(self, x, y, num):
        super(PlayerShoot, self).__init__(x, y, 'assets/One_shot.png')
        self.speed *= -1
        self.scale = 0.2
        self.num = num

    def on_exit(self):
        super(PlayerShoot, self).on_exit()
        PlayerShoot.shoot_check[self.num] = 0

class Enemy(Actor):
    def __init__(self, x, y):
        super(Enemy, self).__init__('assets/Enemy.png', x, y)
        self.scale = 0.05
        self.hp = 5
        self._cshape = cm.AARectShape(self.position,
                                      self.width * 0.025,
                                      self.height * 0.025)
        self.do(ac.Delay(3) + ac.MoveTo((600,400),4) + ac.MoveTo((300,0),4))
