import pygame
import math
import random
import sys

WIDTH, HEIGHT = 800, 800
CENTER = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
HEX_RADIUS = 250
PARTICLE_RADIUS = 3
BALL_RADIUS = 10
GRAVITY = pygame.Vector2(0, 0.25)
FRICTION = 0.98
SPAWN_RATE = 10

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def get_hexagon_points(center, radius, angle_deg):
    return [
        pygame.Vector2(
            center.x + radius * math.cos(math.radians(angle_deg + i * 60)),
            center.y + radius * math.sin(math.radians(angle_deg + i * 60))
        )
        for i in range(6)
    ]

def reflect_and_clamp(obj, hex_points, radius):
    # Keep object inside hexagon
    for i in range(6):
        a = hex_points[i]
        b = hex_points[(i + 1) % 6]
        edge = b - a
        edge_normal = pygame.Vector2(-edge.y, edge.x).normalize()
        to_center = obj.pos - a
        dist = to_center.dot(edge_normal)
        if dist > -radius:
            # Push inside
            obj.pos -= edge_normal * (dist + radius)
            # Reflect velocity
            if obj.vel.dot(edge_normal) > 0:
                continue
            obj.vel -= 2 * obj.vel.dot(edge_normal) * edge_normal
            obj.vel *= 0.8

class Particle:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))

    def update(self):
        self.vel += GRAVITY
        self.vel *= FRICTION
        self.pos += self.vel

    def draw(self, surface, color=(0, 150, 255)):
        pygame.draw.circle(surface, color, self.pos, PARTICLE_RADIUS)

class Ball:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

    def update(self, keys):
        if keys[pygame.K_a]:
            self.vel.x -= 0.4
        if keys[pygame.K_d]:
            self.vel.x += 0.4
        self.vel += GRAVITY
        self.vel *= FRICTION
        self.pos += self.vel

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 100, 100), self.pos, BALL_RADIUS)

# Init
angle = 0
particles = []
ball = Ball(CENTER - pygame.Vector2(0, 100))
confetti_mode = False
c_pressed_last = False

running = True
while running:
    screen.fill((20, 20, 30))
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Easter egg toggle
    if keys[pygame.K_c] and not c_pressed_last:
        confetti_mode = not confetti_mode
    c_pressed_last = keys[pygame.K_c]

    # Rotate hexagon
    angle += 0.5
    hex_points = get_hexagon_points(CENTER, HEX_RADIUS, angle)

    # Spawn water
    if keys[pygame.K_w]:
        for _ in range(SPAWN_RATE):
            particles.append(Particle(CENTER))

    # Update water
    for p in particles:
        p.update()
        reflect_and_clamp(p, hex_points, PARTICLE_RADIUS)
        color = (
            random.choice([(255, 0, 0), (0, 255, 0), (0, 200, 255), (255, 255, 0)])
            if confetti_mode else (0, 150, 255)
        )
        p.draw(screen, color=color)

    # Update ball
    ball.update(keys)
    reflect_and_clamp(ball, hex_points, BALL_RADIUS)
    ball.draw(screen)

    # Draw hexagon
    pygame.draw.polygon(screen, (220, 220, 220), hex_points, 2)

    pygame.display.flip()

pygame.quit()
sys.exit()

