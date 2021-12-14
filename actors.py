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
from gamelayer import *

import pyglet.image
from pyglet.image import Animation

raw = pyglet.image.load('assets/explosion.png')
seq = pyglet.image.ImageGrid(raw, 1, 8)
explosion_img = Animation.from_image_sequence(seq, 0.07, False)

raw2 = pyglet.image.load('assets/bomb_exp.png')
seq2 = pyglet.image.ImageGrid(raw2, 4, 4)
explosion_img2 = Animation.from_image_sequence(seq2, 0.1, False)

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
        self.scale = 1.5
        self.do(ac.Delay(1) + ac.CallFunc(self.kill))

        exp_sound = pygame.mixer.Sound("C:/Users/ahn87/Desktop/dd/2Grade2/게임 프로그래밍 입문/ShootingShooter_GPI_Project/sound/explosion1.wav")
        exp_sound.set_volume(0.1)
        exp_sound.play()

class Bomb_Explosion(Actor):
    def __init__(self, x, y):
        super(Bomb_Explosion, self).__init__(explosion_img2, x, y)
        self.scale = 7
        self.do(ac.Delay(1.8) + ac.CallFunc(self.kill))

        exp_sound = pygame.mixer.Sound("C:/Users/ahn87/Desktop/dd/2Grade2/게임 프로그래밍 입문/ShootingShooter_GPI_Project/sound/bomb_explosion.wav")
        exp_sound.set_volume(0.1)
        exp_sound.play()


class Life_image(Actor):
    def __init__(self, x, y):
        super(Life_image, self).__init__('assets/Player_Character.png', x, y)
        self.scale = 0.08

class Missile_image(Actor):
    def __init__(self, x, y):
        super(Missile_image, self).__init__('assets/missile.png', x, y)
        self.scale = 0.04



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
        self.shootcount = 0
        self.plane_level = 1
        self.shoot_sound = pygame.mixer.Sound(
            "C:/Users/ahn87/Desktop/dd/2Grade2/게임 프로그래밍 입문/ShootingShooter_GPI_Project/sound/shoot.mp3")
        self.shoot_sound.set_volume(0.01)

        #print('player cannon(size,collsize) : ', self.width, self.cshape.r)
        
        #width = height = 51

    def update(self, elapsed):
        pressed = PlayerPlane.KEYS_PRESSED
        space_pressed = pressed[key.SPACE] == 1

        #shoot

        self.elapsed -= elapsed
        if self.elapsed < 0.1 and space_pressed:
            self.elapsed = 0.4
            self.shootcount += 1
            self.shoot_sound.play()
            if(self.shootcount >= 14):
                self.shootcount = 0
            if self.plane_level == 1:
                PlayerShoot.shoot_check[self.shootcount] = PlayerShoot(self.x, self.y + 40, self.shootcount)
                self.parent.add(PlayerShoot.shoot_check[self.shootcount])
            else:
                PlayerShoot2.shoot_check[self.shootcount] = PlayerShoot2(self.x, self.y + 40, self.shootcount)
                self.parent.add(PlayerShoot2.shoot_check[self.shootcount])

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
            self.parent.add(Explosion(self.position[0], self.position[1]))
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
        self.scale = 2.0
        if atk_type == 1:
            self.speed = eu.Vector2(0, -200)
        if atk_type == 2:
            self.speed = eu.Vector2(50, -180)
        if atk_type == 3:
            self.speed = eu.Vector2(-50, -180)


class Missile(Actor):
    def __init__(self, x, y):
        super(Missile, self).__init__('assets/missile.png', x, y)
        self.scale = 0.05
        self.scale_y = 0.8
        self.do(ac.MoveTo((300,400), 4) + ac.CallFunc(self.callpardeal) + ac.CallFunc(self.kill))
        exp_sound = pygame.mixer.Sound("C:/Users/ahn87/Desktop/dd/2Grade2/게임 프로그래밍 입문/ShootingShooter_GPI_Project/sound/bomb_move.wav")
        exp_sound.set_volume(0.1)
        exp_sound.play()

    def callpardeal(self):
        self.parent.bomb_boom()

class PlayerShoot(Shoot):
    shoot_check = [0 for i in range(15)]

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
        if isinstance(other, Enemy) or isinstance(other, Boss):
            other.hit(self.atk)
            self.kill()

class PlayerShoot2(Shoot):
    shoot_check = [0 for i in range(15)]

    def __init__(self, x, y, num):
        super(PlayerShoot2, self).__init__(x, y, 'assets/Two_Shot.png')
        self.speed *= -1
        self.scale = 0.2
        self.num = num
        self.atk = 2

    def on_exit(self):
        super(PlayerShoot2, self).on_exit()
        PlayerShoot2.shoot_check[self.num] = 0

    def collide(self, other):
        if isinstance(other, Enemy) or isinstance(other, Boss2):
            other.hit(self.atk)
            self.kill()

class Boss(Actor):
    def __init__(self, x, y):
        super(Boss, self).__init__('assets/Enemy.png', x, y)
        self.scale = 0.4
        self.hp = 5
        self.delay = 0
        self.scale_y = 0.4
        self.death = 0
        self.explosion_count = 0
        self._cshape = cm.CircleShape(self.position,
                                      self.width * 0.25)
        self.do(ac.MoveTo((300, 680), 5))
        # print('player enemy(size,collsize) : ', self.width, self.cshape.center, self.cshape.rx, self.cshape.ry)

    def update(self, dt):
        self.delay += dt
        if self.delay > 4:
            self.delay = 0
            self.parent.add(EnemyShoot(self.x + 30, self.y, 1))
            self.parent.add(EnemyShoot(self.x + 30, self.y, 2))
            self.parent.add(EnemyShoot(self.x + 30, self.y, 3))
            self.parent.add(EnemyShoot(self.x - 30, self.y, 1))
            self.parent.add(EnemyShoot(self.x - 30, self.y, 2))
            self.parent.add(EnemyShoot(self.x - 30, self.y, 3))

    def hit(self, damage=1):
        self.hp -= damage
        self.do(Hit())
        if self.hp <= 0 and self.is_running:
            self.explode()

    def explode(self):
        if(self.death == 0):
            self.do(ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) +
                    ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) +
                    ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) +
                    ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) +
                    ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) +
                    ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) + ac.CallFunc(self.kill) +
                    ac.CallFunc(self.level_up_call))
            self.death = 1

    def boss_explosion(self):
        self.explosion_count += 1
        if(self.explosion_count == 1):
            self.parent.add(Explosion(self.position[0], self.position[1] - 100))
            self.parent.add(Explosion(self.position[0] - 20, self.position[1]))
        if(self.explosion_count == 2):
            self.parent.add(Explosion(self.position[0] + 30, self.position[1]))
        if(self.explosion_count == 3):
            self.parent.add(Explosion(self.position[0] + 50, self.position[1]))
            self.parent.add(Explosion(self.position[0] - 20, self.position[1]))
        if(self.explosion_count == 4):
            self.parent.add(Explosion(self.position[0] + 20, self.position[1] - 30))
        if(self.explosion_count == 5):
            self.parent.add(Explosion(self.position[0] - 50, self.position[1]))
            self.parent.add(Explosion(self.position[0] + 30, self.position[1] + 30))
        if(self.explosion_count == 6):
            self.parent.add(Explosion(self.position[0], self.position[1] - 20))
            self.parent.add(Explosion(self.position[0] + 20, self.position[1]))

    def level_up_call(self):
        self.parent.level_up()

class Boss2(Actor):
    def __init__(self, x, y):
        super(Boss2, self).__init__('assets/boss_shadow.png', x, y)
        self.scale = 2.5
        self.hp = 50
        self.delay = 0
        self.death = 0
        self.explosion_count = 0
        self.speed = eu.Vector2(80,0)
        self._cshape = cm.AARectShape(self.position,
                                      self.width * 0.2,
                                      self.height * 0.3)
        self.do(ac.MoveTo((300, 730), 3))
        self.direction = 1
        # print('player enemy(size,collsize) : ', self.width, self.cshape.center, self.cshape.rx, self.cshape.ry)

    def update(self, dt):
        self.delay += dt
        self.move(self.speed * dt * self.direction)
        if self.x >= 450:
            self.direction = -1
        elif self.x <= 150:
            self.direction = 1
        if self.delay > 4:
            self.delay = 0
            self.parent.add(EnemyShoot(self.x + 50, self.y - 100, 1))
            self.parent.add(EnemyShoot(self.x + 50, self.y - 100, 2))
            self.parent.add(EnemyShoot(self.x + 50, self.y - 100, 3))
            self.parent.add(EnemyShoot(self.x - 50, self.y - 100, 1))
            self.parent.add(EnemyShoot(self.x - 50, self.y - 100, 2))
            self.parent.add(EnemyShoot(self.x - 50, self.y - 100, 3))
            self.parent.add(EnemyShoot(self.x, self.y - 100, 1))
            self.parent.add(EnemyShoot(self.x, self.y - 100, 2))
            self.parent.add(EnemyShoot(self.x, self.y - 100, 3))

    def hit(self, damage=1):
        self.hp -= damage
        self.do(Hit())
        if self.hp <= 0 and self.is_running:
            self.direction = 0
            self.explode()

    def explode(self):
        if(self.death == 0):
            self.do(ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) +
                    ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) +
                    ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) +
                    ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) +
                    ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) +
                    ac.CallFunc(self.boss_explosion) + ac.Delay(0.4) + ac.CallFunc(self.kill) +
                    ac.CallFunc(self.finish_game))
            self.death = 1

    def boss_explosion(self):
        self.explosion_count += 1
        if(self.explosion_count == 1):
            self.parent.add(Explosion(self.position[0], self.position[1] - 150))
            self.parent.add(Explosion(self.position[0] - 20, self.position[1] - 50))
            self.parent.add(Explosion(self.position[0] + 60, self.position[1] - 50))
        if(self.explosion_count == 2):
            self.parent.add(Explosion(self.position[0] + 30, self.position[1] - 50))
            self.parent.add(Explosion(self.position[0] - 70, self.position[1] - 50))
        if(self.explosion_count == 3):
            self.parent.add(Explosion(self.position[0] + 120, self.position[1] - 50))
            self.parent.add(Explosion(self.position[0] - 20, self.position[1] - 50))
        if(self.explosion_count == 4):
            self.parent.add(Explosion(self.position[0] + 20, self.position[1] - 80))
        if(self.explosion_count == 5):
            self.parent.add(Explosion(self.position[0] - 120, self.position[1] - 50))
            self.parent.add(Explosion(self.position[0] + 30, self.position[1] - 80))
        if(self.explosion_count == 6):
            self.parent.add(Explosion(self.position[0], self.position[1] - 70))
            self.parent.add(Explosion(self.position[0] + 20, self.position[1] - 50))

    def finish_game(self):
        print("end")

class Enemy(Actor):
    direction = 0
    def __init__(self, x, y):
        super(Enemy, self).__init__('assets/Boss_Plane.png', x, y)
        self.hp = 5
        self.delay = 0
        self._cshape = cm.AARectShape(self.position,
                                      self.width * 0.4,
                                      self.height * 0.4)
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
        self.parent.add(Explosion(self.position[0], self.position[1]))
        self.kill()

class Hit(ac.IntervalAction):
    def init(self, duration=0.5):
        self.duration = duration
    def update(self, t):
        self.target.color = (255, 255 * t, 255 * t)
