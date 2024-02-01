import pygame as py 
import time, random


class Camera:
    def __init__(self):
        self.scroll = [0, 0]
        self.true_scroll = [0, 0]
    
    def update(self, obj, delta_time):
        self.dt = delta_time

        self.scroll[0] += (obj.rect.x - self.scroll[0] - screen.get_width() / 2) / 8 * self.dt
        self.scroll[1] += (obj.rect.y - self.scroll[1] - screen.get_height() / 2) / 8 * self.dt

        self.true_scroll = self.scroll.copy()
        self.true_scroll[0] = int(self.true_scroll[0])
        self.true_scroll[1] = int(self.true_scroll[1])

class Tile:
    def __init__(self, pos, size, color=(155, 105, 50)):
        self.pos = pos
        self.image = py.Surface((size, size), py.SRCALPHA)
        self.image.fill(color)
        self.rect = py.Rect(self.pos[0] * size, self.pos[1] * size, size, size)
    
    def render(self, camera_offset, scroll=[1, 1]):
        render_x = self.rect.x - camera_offset[0] * scroll[0]
        render_y = self.rect.y - camera_offset[1] * scroll[1]
        return self.image, (render_x, render_y)
    
class Player(py.sprite.Sprite):
    def __init__(self, pos, size):
        self.image = py.Surface((size, size)).convert()
        self.image.fill((0, 250, 0))
        self.x, self.y = pos
        self.x *= size
        self.y *= size
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        self.vel = [0, 0]
        self.gravity = 0.25
    
    def apply_gravity(self):
        self.vel[1] += self.gravity * self.dt
        if self.vel[1] > 10:
            self.vel[1] = 10
    
    def controls(self):
        key = py.key.get_pressed()
        if key[py.K_d]:
            self.vel[0] = 5
        elif key[py.K_a]:
            self.vel[0] = -5
        else:
            self.vel[0] = 0
        
        if key[py.K_SPACE]:
            self.vel[1] = -10
        
    def move(self, chunks):
        self.y += self.vel[1] * self.dt
        self.rect.y = self.y

        for chunk in chunks:
            for tile in chunk:
                if tile.rect.colliderect(self.rect):
                    if self.vel[1] > 0:
                        self.y = tile.rect.y - self.rect.h
                    elif self.vel[1] < 0:
                        self.y = tile.rect.bottom
                    self.vel[1] = 0
        
        self.rect.y = self.y


        self.x += self.vel[0] * self.dt
        self.rect.x = self.x
        
        for chunk in chunks:
            for tile in chunk:
                if tile.rect.colliderect(self.rect):
                    if self.vel[0] > 0:
                        self.x = tile.rect.x - self.rect.w
                    elif self.vel[0] < 0:
                        self.x = tile.rect.right

        self.rect.x = self.x
        
    def render(self, camera_offset):
        render_x = self.rect.x - camera_offset[0]
        render_y = self.rect.y - camera_offset[1]
        screen.blit(self.image, (render_x, render_y))

    def update(self, delta_time):
        self.dt = delta_time
        self.apply_gravity()
        self.controls()

py.init()

screen = py.display.set_mode((1200, 720))
clock = py.time.Clock()

font = py.font.Font(None, 32)

camera = Camera()
player = Player((0, -5), 24)
tiles = {}

chunks = {
    # x;y : [chunk tiles]
}
chunk_size = 768, 432

last_time = time.perf_counter()
dt_setting = 60 
dt = 0

# size
row = 100
col = 30

for x in range(row):
    for y in range(col):
        tiles[str(x) + ';' + str(y)] = Tile((x, y), 48, random.choice([(155, 105, 50), (56, 214, 125)]))

# pre organize chunk
for loc in tiles:
    x, y = tiles[loc].rect.x // chunk_size[0], tiles[loc].rect.y // chunk_size[1]
    if str(x) + ';' + str(y) not in chunks:
        chunks[str(x) + ';' + str(y)] = set()
    chunks[str(x) + ';' + str(y)].add(tiles[loc])


while True:
    dt = time.perf_counter() - last_time
    dt *= dt_setting
    last_time = time.perf_counter()
    if dt > 1:
        dt = 1

    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            exit()

    screen.fill((30, 30, 30,))

    camera.update(player, dt)

    player.update(dt)

    neighbor_offsets = [
            str(player.rect.x // chunk_size[0] - 1) + ';' + str(player.rect.y // chunk_size[1] - 1), # topleft chunk
            str(player.rect.x // chunk_size[0]) + ';' + str(player.rect.y // chunk_size[1] - 1), # top chunk
            str(player.rect.x // chunk_size[0] + 1) + ';' + str(player.rect.y // chunk_size[1] - 1), # topright chunk

            str(player.rect.x // chunk_size[0] - 1) + ';' + str(player.rect.y // chunk_size[1]), # left chunk
            str(player.rect.x // chunk_size[0]) + ';' + str(player.rect.y // chunk_size[1]), # middle chunk
            str(player.rect.x // chunk_size[0] + 1) + ';' + str(player.rect.y // chunk_size[1]), # right chunk

            str(player.rect.x // chunk_size[0] - 1) + ';' + str(player.rect.y // chunk_size[1] + 1), # bottomleft chunk
            str(player.rect.x // chunk_size[0]) + ';' + str(player.rect.y // chunk_size[1] + 1), # bottom chunk
            str(player.rect.x // chunk_size[0] + 1) + ';' + str(player.rect.y // chunk_size[1] + 1) # bottomright chunk
            ]

    collision_chunks = []
    for offset in neighbor_offsets:
        try:
            screen.blits([tile.render(camera.true_scroll) for tile in chunks[offset]])
        except:
            pass
        collision_chunks.append(chunks.get(offset, []))
    
    # player collision with only tiles around player (chunks)
    player.move(collision_chunks)

    player.render(camera.true_scroll)

    screen.blit(font.render(f"FPS: {clock.get_fps():.1f}", True, 'white'), (10, 10))
    screen.blit(font.render(f"Tiles: {len(tiles)}", True, 'white'), (10, 42))

    py.display.flip()
    clock.tick(1000)
