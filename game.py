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
SPAWN_RATE = 10  # Water particles per frame when W is held

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

def reflect_velocity(pos, vel, p1, p2):
    edge = p2 - p1
    normal = pygame.Vector2(-edge.y, edge.x).normalize()
    to_particle = pos - p1
    if normal.dot(to_particle) < 0:
        normal = -normal
    if normal.dot(vel) < 0:
        vel -= 2 * vel.dot(normal) * normal
        vel *= 0.8
    return vel

def is_inside_hex(pos, hex_points):
    total = 0
    for i in range(6):
        p1, p2 = hex_points[i], hex_points[(i + 1) % 6]
        if ((p1.y > pos.y) != (p2.y > pos.y)) and \
           (pos.x < (p2.x - p1.x) * (pos.y - p1.y) / (p2.y - p1.y + 1e-9) + p1.x):
            total += 1
    return total % 2 == 1

def handle_wall_collision(particle, hex_points):
    if not is_inside_hex(particle.pos, hex_points):
        closest_dist = float('inf')
        closest_edge = None
        for i in range(6):
            a = hex_points[i]
            b = hex_points[(i + 1) % 6]
            proj = max(0, min(1, ((particle.pos - a).dot(b - a)) / (b - a).length_squared()))
            closest = a + proj * (b - a)
            dist = (particle.pos - closest).length_squared()
            if dist < closest_dist:
                closest_dist = dist
                closest_edge = (a, b)
        if closest_edge:
            particle.vel = reflect_velocity(particle.pos, particle.vel, *closest_edge)

class Particle:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))

    def update(self):
        self.vel += GRAVITY
        self.vel *= FRICTION
        self.pos += self.vel

    def draw(self, surface):
        pygame.draw.circle(surface, (0, 150, 255), self.pos, PARTICLE_RADIUS)

class Ball:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(0, 0)

    def update(self, keys):
        if keys[pygame.K_a]:
            self.vel.x -= 0.5
        if keys[pygame.K_d]:
            self.vel.x += 0.5
        self.vel += GRAVITY
        self.vel *= FRICTION
        self.pos += self.vel

    def draw(self, surface):
        pygame.draw.circle(surface, (255, 100, 100), self.pos, BALL_RADIUS)

    def collide_with_hex(self, hex_points):
        handle_wall_collision(self, hex_points)

# Initialize
angle = 0
particles = []
ball = Ball(CENTER - pygame.Vector2(0, 100))

running = True
while running:
    screen.fill((15, 15, 25))
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rotate hex
    angle += 0.5
    hex_points = get_hexagon_points(CENTER, HEX_RADIUS, angle)

    # Spawn water
    if keys[pygame.K_w]:
        for _ in range(SPAWN_RATE):
            particles.append(Particle(CENTER))

    # Update water particles
    for p in particles:
        p.update()
        handle_wall_collision(p, hex_points)
        p.draw(screen)

    # Update and draw ball
    ball.update(keys)
    ball.collide_with_hex(hex_points)
    ball.draw(screen)

    # Draw hexagon
    pygame.draw.polygon(screen, (200, 200, 200), hex_points, 2)

    pygame.display.flip()

pygame.quit()
sys.exit()

