import pygame as py 
import time, random, math, noise

random.seed(10) 

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
            self.vel[0] = 15
        elif key[py.K_a]:
            self.vel[0] = -15
        else:
            self.vel[0] = 0
        
        if key[py.K_SPACE]:
            self.vel[1] = -10
        
    def move(self, chunks):
        self.y += self.vel[1] * self.dt
        self.rect.y = self.y

        for tiles in chunks:
            for tile in tiles:
                if tile.rect.colliderect(self.rect):
                    if self.vel[1] > 0:
                        self.y = tile.rect.y - self.rect.h
                    elif self.vel[1] < 0:
                        self.y = tile.rect.bottom
                    self.vel[1] = 0
        
        self.rect.y = self.y


        self.x += self.vel[0] * self.dt
        self.rect.x = self.x
        
        for tiles in chunks:
            for tile in tiles:
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

def generate_chunk(offset, chunk_size):
    offset = offset.split(';')
    offset[0] = int(offset[0]) * chunk_size[0]
    offset[1] = int(offset[1]) * chunk_size[1]

    tiles = []
    for x in range(chunk_size[0] // tile_size):
        is_first_tile = True
        for y in range(chunk_size[1] // tile_size):
            color = random.choice([(155, 105, 50), (135, 75, 50)])
            # if y < 1:
            #     color = (56, 214, 125)

            target_x = x + offset[0] // tile_size
            target_y = y + offset[1] // tile_size 
            height = int(noise.pnoise1(target_x * 0.1, repeat=99999) * 5)
            if target_y > height:
                if is_first_tile:
                    color = (56, 214, 125)
                    is_first_tile = False
                tiles.append(Tile((target_x, target_y), tile_size, color))
    return tiles

py.init()

screen = py.display.set_mode((1200, 720), py.RESIZABLE)
clock = py.time.Clock()

font = py.font.Font(None, 32)

camera = Camera()
player = Player((0, -5), 24)
tiles = {}
background = []

tile_size = 48

chunks = {
    # x;y : [chunk tiles]
}
chunk_size = 18 * tile_size, 16 * tile_size

last_time = time.perf_counter()
dt_setting = 60 
dt = 0

# size
# row = 18
# col = 16

# # for x in range(row):
# #     for y in range(col):
# #         color = random.choice([(155, 105, 50), (135, 75, 50)])
# #         if y < 1:
# #             color = (56, 214, 125)
# #         tiles[str(x) + ';' + str(y)] = Tile((x, y), tile_size, color)
# #         # print(str(x) + ';' + str(y))

# #         # if random.randint(0, 100) == 0:
# #         #     background.append(Tile((x, y-y//20), random.choice([48, 64, 128]), random.choice([(192, 168, 127), (56, 214, 125)])))

# # count_tiles = len(tiles)

# # pre organize chunk
# for loc in tiles.copy():
#     x, y = tiles[loc].rect.x // chunk_size[0], tiles[loc].rect.y // chunk_size[1]
#     if str(x) + ';' + str(y) not in chunks:
#         chunks[str(x) + ';' + str(y)] = set()
#     chunks[str(x) + ';' + str(y)].add(tiles[loc])
#     del tiles[loc]


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
    neighbor_chunk_offsets = [
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
    for offset in neighbor_chunk_offsets:
        try:
            screen.blits([tile.render(camera.true_scroll) for tile in chunks[offset]])
        except KeyError:
            if int(offset.split(';')[1]) > -1:
                chunks[offset] = generate_chunk(offset, chunk_size)
        
        py.draw.rect(screen, 'white', py.Rect(int(offset.split(';')[0]) * chunk_size[0] - camera.true_scroll[0], int(offset.split(';')[1]) * chunk_size[1] - camera.true_scroll[1], chunk_size[0], chunk_size[1]), 1)
        collision_chunks.append(chunks.get(offset, []))
    
    [chunks.pop(keys_offset) for keys_offset in chunks.copy() if keys_offset not in neighbor_chunk_offsets] # remove unnecessary chunks to get stable memory usage
    
    # player collision with only tiles around player (chunks)
    player.move(collision_chunks)

    player.render(camera.true_scroll)

    screen.blit(font.render(f"FPS: {clock.get_fps():.1f}", True, 'white'), (10, 10))
    screen.blit(font.render(f"Tiles: {len(chunks) * 16 * 16}", True, 'white'), (10, 42))
    screen.blit(font.render(f"{player.rect.center}", True, 'white'), (10, 72))

    py.display.flip()
    clock.tick(1000)

