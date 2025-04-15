import pygame
import math
import random
import sys

WIDTH, HEIGHT = 800, 800
CENTER = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
HEX_RADIUS = 250
PARTICLE_RADIUS = 3
GRAVITY = pygame.Vector2(0, 0.2)
FRICTION = 0.98
SPAWN_RATE = 10  # particles per frame when holding W

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

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

def get_hexagon_points(center, radius, angle_deg):
    points = []
    for i in range(6):
        angle = math.radians(angle_deg + i * 60)
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        points.append(pygame.Vector2(x, y))
    return points

def reflect_velocity(pos, vel, p1, p2):
    edge = p2 - p1
    normal = pygame.Vector2(-edge.y, edge.x).normalize()
    to_particle = pos - p1
    if normal.dot(to_particle) < 0:
        normal = -normal  # ensure it points inward
    if normal.dot(vel) < 0:  # only reflect if moving toward wall
        vel -= 2 * vel.dot(normal) * normal
        vel *= 0.8  # dampen bounce
    return vel

def is_inside_hex(pos, hex_points):
    total = 0
    for i in range(6):
        p1 = hex_points[i]
        p2 = hex_points[(i + 1) % 6]
        if ((p1.y > pos.y) != (p2.y > pos.y)) and \
           (pos.x < (p2.x - p1.x) * (pos.y - p1.y) / (p2.y - p1.y + 1e-9) + p1.x):
            total += 1
    return total % 2 == 1

angle = 0
particles = []

running = True
while running:
    screen.fill((10, 10, 20))
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rotate the hexagon
    angle += 0.5
    hex_points = get_hexagon_points(CENTER, HEX_RADIUS, angle)

    # Spawn particles in center
    if keys[pygame.K_w]:
        for _ in range(SPAWN_RATE):
            particles.append(Particle(CENTER))

    # Update and handle collisions
    for p in particles:
        p.update()

        if not is_inside_hex(p.pos, hex_points):
            # Find nearest hex edge and reflect
            closest_dist = float('inf')
            closest_edge = None
            for i in range(6):
                a = hex_points[i]
                b = hex_points[(i + 1) % 6]
                proj = max(0, min(1, ((p.pos - a).dot(b - a)) / (b - a).length_squared()))
                closest = a + proj * (b - a)
                dist = (p.pos - closest).length_squared()
                if dist < closest_dist:
                    closest_dist = dist
                    closest_edge = (a, b)
            if closest_edge:
                p.vel = reflect_velocity(p.pos, p.vel, *closest_edge)

        p.draw(screen)

    # Draw hexagon
    pygame.draw.polygon(screen, (200, 200, 200), hex_points, 2)

    pygame.display.flip()

pygame.quit()
sys.exit()
