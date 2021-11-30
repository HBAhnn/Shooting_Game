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

import random

import pyglet.image
from pyglet.image import Animation

raw = pyglet.image.load('assets/explosion.png')
seq = pyglet.image.ImageGrid(raw, 1, 8)
explosion_img = Animation.from_image_sequence(seq, 0.07, False)

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

    def hit(self):
        self.kill()
    
class Explosion(Actor):
    def __init__(self, x, y):
        super(Explosion, self).__init__(explosion_img, x, y)
        self.do(ac.Delay(1) + ac.CallFunc(self.kill))


class PlayerPlane(Actor):
    KEYS_PRESSED = defaultdict(int)
    Guardtime = 3

    def __init__(self, x, y):
        super(PlayerPlane, self).__init__('assets/Player_Character.png', x, y)
        self.scale = 0.1
        self.Xspeed = eu.Vector2(200, 0)
        self.Yspeed = eu.Vector2(0, 200)
        self.elapsed = 0
        self.do(ac.Blink(6,3))
        self.cshape.r *= 0.1

        #print('player cannon(size,collsize) : ', self.width, self.cshape.r)
        
        #width = height = 51

    def update(self, elapsed):
        pressed = PlayerPlane.KEYS_PRESSED
        space_pressed = pressed[key.SPACE] == 1

        #shoot
        self.elapsed -= elapsed
        if self.elapsed < 0.1 and space_pressed:
            self.elapsed = 0.3
            for i in range(30):
                if PlayerShoot.shoot_check[i] == 0:
                    PlayerShoot.shoot_check[i] = PlayerShoot(self.x, self.y + 40, i)
                    self.parent.add(PlayerShoot.shoot_check[i])
                    break

        #move
        movable = 1
        Xmovement = pressed[key.RIGHT] - pressed[key.LEFT]
        Ymovement = pressed[key.UP] - pressed[key.DOWN]
        if Xmovement > 0 and self.x >= self.parent.width:
            movable = 0
        if Xmovement < 0 and 0 >= self.x:
            movable = 0
        if Ymovement < 0 and self.y <= 0:
            movable = 0
        if movable == 1:
            self.move(self.Xspeed * Xmovement * elapsed, self.Yspeed * Ymovement * elapsed)

    def move(self, Xmove, Ymove):
        self.position += Xmove
        self.position += Ymove

    def collide(self, other):
        other.hit()
        if PlayerPlane.Guardtime < 0:
            self.kill()

class Shoot(Actor):
    def __init__(self, x, y, img='assets/Enemy_shoot_real.png'):
        super(Shoot, self).__init__(img, x, y)
        self.speed = eu.Vector2(0, -400)

    def update(self, elapsed):
        self.move(self.speed * elapsed)

class EnemyShoot(Shoot):
    def __init__(self, x, y, atk_type = 1):
        super(EnemyShoot, self).__init__(x, y, 'assets/Enemy_shoot_real.png')
        if atk_type == 1:
            self.speed = eu.Vector2(0, -200)
        if atk_type == 2:
            self.speed = eu.Vector2(50, -150)
        if atk_type == 3:
            self.speed = eu.Vector2(-50, -150)

class PlayerShoot(Shoot):
    shoot_check = [0 for i in range(30)]

    def __init__(self, x, y, num):
        super(PlayerShoot, self).__init__(x, y, 'assets/One_shot.png')
        self.speed *= -1
        self.scale = 0.2
        self.num = num
        self.atk = 1
        #print('player shoot(size,collsize) : ', self.width, self.cshape.r)

    def on_exit(self):
        super(PlayerShoot, self).on_exit()
        PlayerShoot.shoot_check[self.num] = 0

    def collide(self, other):
        if isinstance(other, Enemy):
            other.hit(self.atk)
            self.kill()

class Enemy(Actor):
    direction = 0
    def __init__(self, x, y):
        super(Enemy, self).__init__('assets/Enemy.png', x, y)
        self.scale = 0.1
        self.hp = 5
        self.delay = 0
        self._cshape = cm.AARectShape(self.position,
                                      self.width * 0.05,
                                      self.height * 0.05)
        #print('player enemy(size,collsize) : ', self.width, self.cshape.center, self.cshape.rx, self.cshape.ry)
        if Enemy.direction == 0:
            Enemy.direction = 1
            self.do(ac.MoveTo((600,350),8) + ac.MoveTo((300,-50),8) + ac.CallFunc(self.kill))
        elif Enemy.direction == 1:
            Enemy.direction = 0
            self.do(ac.MoveTo((0,350),8) + ac.MoveTo((300,-50),8) + ac.CallFunc(self.kill))

    def update(self, dt):
        self.delay += dt
        if random.random() < 0.003 and self.delay > 2:
            self.delay = 0
            self.parent.add(EnemyShoot(self.x, self.y, 1))
            self.parent.add(EnemyShoot(self.x, self.y, 2))
            self.parent.add(EnemyShoot(self.x, self.y, 3))

    def hit(self, damage = 1):
        self.hp -= damage
        self.do(Hit())
        if self.hp <= 0 and self.is_running:
            self.explode()
        

    def explode(self):
        self.parent.Explose(self.position)
        self.kill()

class Hit(ac.IntervalAction):
    def init(self, duration=0.5):
        self.duration = duration

    def update(self, t):
        self.target.color = (255, 255 * t, 255 * t)
