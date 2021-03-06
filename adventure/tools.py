import pygame
import pytmx
from settings import *
import xml.etree.ElementTree as ET

def draw_player_health(surface, x, y, pct):
    if pct < 0:
        pct = 0
    fill = pct * HEALTH_BAR_LENGTH
    outline_rect = pygame.Rect(x, y, HEALTH_BAR_LENGTH, HEALTH_BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, HEALTH_BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pygame.draw.rect(surface, col, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def collide_with_walls(sprite, group, dir):
        if dir == 'x':
            hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if sprite.hit_rect.centerx > hits[0].rect.centerx:
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                if sprite.hit_rect.centerx < hits[0].rect.centerx:
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                sprite.hit_rect.centerx = sprite.pos.x
                sprite.vel.x = 0
        if dir == 'y':
            hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if sprite.hit_rect.centery > hits[0].rect.centery:
                    sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
                if sprite.hit_rect.centery < hits[0].rect.centery:
                    sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                sprite.hit_rect.centery = sprite.pos.y
                sprite.vel.y = 0

class TiledMap:
    def __init__(self, filename):
        self.data = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = self.data.width * self.data.tilewidth
        self.height = self.data.height * self.data.tileheight
        self.image = pygame.Surface((self.width, self.height))
        for layer in self.data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, tile in layer.tiles():
                    self.image.blit(tile, (x * self.data.tilewidth, y * self.data.tileheight))
        self.rect = self.image.get_rect()

class Spritesheet:
    def __init__(self, filename):
        # filename - without extension, find matching xml
        self.spritesheet = pygame.image.load(filename + '.png').convert_alpha()
        if path.isfile(filename + '.xml'):
            tree = ET.parse(filename + '.xml')
            self.map = {}
            # read xml and pull out desired values (x, y, w, h)
            for node in tree.iter():
                if node.attrib.get('name'):
                    name = node.attrib.get('name')
                    self.map[name] = {}
                    self.map[name]['x'] = int(node.attrib.get('x'))
                    self.map[name]['y'] = int(node.attrib.get('y'))
                    self.map[name]['w'] = int(node.attrib.get('width'))
                    self.map[name]['h'] = int(node.attrib.get('height'))

    def get_image_by_name(self, name):
        rect = pygame.Rect(self.map[name]['x'], self.map[name]['y'],
                           self.map[name]['w'], self.map[name]['h'])
        return self.spritesheet.subsurface(rect)

    def get_image_by_rect(self, x, y, w, h):
        rect = pygame.Rect(x, y, w, h)
        return self.spritesheet.subsurface(rect)

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
        x = min(0, x)
        y = min(0, y)
        x = max(WIDTH - self.width, x)
        y = max(HEIGHT - self.height, y)
        self.camera = pygame.Rect(x, y, self.width, self.height)

    def apply(self, object):
        return object.rect.move(self.camera.topleft)
