import pygame
import os
import time
import random
from pygame import mixer

#initialize pygame
pygame.init()

#initialize font
pygame.font.init()

#global score variable
score = 0

#create window
WIDTH,HEIGHT = 750,750
win = pygame.display.set_mode((WIDTH,HEIGHT))

#set caption 
pygame.display.set_caption("SPACE SHOOTER")

#set icon
icon = pygame.image.load(os.path.join("assets","icon.png"))
pygame.display.set_icon(icon)

# load space ship images
#enemy ship
'''
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))
'''
#new enemy ship
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets","red.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","green.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","blue.png"))

#player ship
#YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_yellow.png"))
#new player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets","player.png"))

#lasers
'''
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))
'''
#new missile
RED_LASER = pygame.image.load(os.path.join("assets","bomb_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","bomb_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","bomb_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","bomb_player.png"))

#background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")),(WIDTH,HEIGHT))

#background music
mixer.music.load(os.path.join("assets","outer-space-warning.wav"))
mixer.music.play(-1)

#Laser Class
class Laser:
    #initialize of Laser class
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        win.blit(self.img, (self.x, self.y))
    
    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(self, obj)

#Ship Class
class Ship:
    COOLDOWN = 30

    #initialize of Ship class
    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        win.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(win)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 8, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

#Player Class
class Player(Ship):

    #initialize of Player class
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        global score
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        score += 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

#Enemy Class
class Enemy(Ship):

    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),    
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER) 
                }

    #initialize of Enemy class 
    def __init__(self, x, y, color, health =100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 10, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
    
#collide function
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#main function
def main():
    
    run = True
    FPS = 60
    level = 0
    lives = 5
    global score
    score = 0

    main_font = pygame.font.SysFont("comicsans",50)
    lost_font = pygame.font.SysFont("comicsans",80)
    
    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 8

    player = Player(300,620)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        win.blit(BG, (0,0))
        #draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {score}", 1, (255,255,255))

        win.blit(lives_label,(10,10))
        win.blit(level_label,(WIDTH - level_label.get_width()-10,10))
        win.blit(score_label,(WIDTH - score_label.get_width()-10,50))

        for enemy in enemies:
            enemy.draw(win)
        
        player.draw(win)

        if lost:
            lost_label = lost_font.render("YOU LOST !!", 1, (255, 255, 255))
            win.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level +=1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:    #LEFT
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:    #RIGHT
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:    #UP
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:    #DOWN
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        

        player.move_lasers(-laser_vel, enemies)

#main screen function
def main_menu():
    run = True
    title_font1 = pygame.font.SysFont("comicsans", 60)
    title_font2 = pygame.font.SysFont("comicsans", 40)
    while run:
        win.blit(BG, (0,0))
        title_label1 = title_font1.render("WELCOME TO SPACE SHOOTER", 1, (255, 255, 255))
        win.blit(title_label1,(WIDTH/2 - title_label1.get_width()/2, 290))
        title_label2 = title_font2.render("Press anykey to begin...", 1, (255, 255, 255))
        win.blit(title_label2,(WIDTH/2 - title_label2.get_width()/2, 360))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                    main()
    
    pygame.quit()

            
#calling main screen function
main_menu()
