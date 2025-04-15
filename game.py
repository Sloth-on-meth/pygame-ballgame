import pygame
import math
import sys

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
BALL_RADIUS = 10
g = 500  # gravity px/s^2
friction = 0.99  # velocity damping
hexagon_radius = 250
rotation_speed = math.radians(30)  # degrees per second

# Ball
ball_pos = [WIDTH // 2, HEIGHT // 2 - 100]
ball_vel = [100, 0]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)


def rotate_point(cx, cy, angle, px, py):
    s, c = math.sin(angle), math.cos(angle)
    px -= cx
    py -= cy
    xnew = px * c - py * s
    ynew = px * s + py * c
    return cx + xnew, cy + ynew


def get_hexagon(center, radius, angle):
    cx, cy = center
    return [
        rotate_point(cx, cy, angle + math.radians(i * 60), cx + radius, cy)
        for i in range(6)
    ]


def reflect_vector(vel, normal):
    dot = vel[0]*normal[0] + vel[1]*normal[1]
    return [
        vel[0] - 2 * dot * normal[0],
        vel[1] - 2 * dot * normal[1]
    ]

angle = 0
running = True
while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update angle
    angle += rotation_speed * dt

    # Update velocity and position
    ball_vel[1] += g * dt
    ball_vel[0] *= friction
    ball_vel[1] *= friction
    ball_pos[0] += ball_vel[0] * dt
    ball_pos[1] += ball_vel[1] * dt

    # Collision with hexagon
    hexagon = get_hexagon((WIDTH // 2, HEIGHT // 2), hexagon_radius, angle)
    for i in range(6):
        p1 = hexagon[i]
        p2 = hexagon[(i + 1) % 6]

        # Line segment vector and normal
        edge = (p2[0] - p1[0], p2[1] - p1[1])
        edge_len = math.hypot(*edge)
        if edge_len == 0:
            continue
        edge_unit = (edge[0] / edge_len, edge[1] / edge_len)
        normal = (-edge_unit[1], edge_unit[0])

        # Distance from ball to line
        rel = (ball_pos[0] - p1[0], ball_pos[1] - p1[1])
        dist = rel[0]*normal[0] + rel[1]*normal[1]

        # Project point onto edge
        proj_len = rel[0]*edge_unit[0] + rel[1]*edge_unit[1]
        if -BALL_RADIUS < dist < BALL_RADIUS and 0 <= proj_len <= edge_len:
            # Move out of wall
            overlap = BALL_RADIUS - dist
            ball_pos[0] += normal[0] * overlap
            ball_pos[1] += normal[1] * overlap
            ball_vel = reflect_vector(ball_vel, normal)

    # Draw
    screen.fill((10, 10, 30))
    pygame.draw.polygon(screen, (200, 200, 255), hexagon, 2)
    pygame.draw.circle(screen, (255, 50, 50), (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)
    pygame.display.flip()

pygame.quit()
sys.exit()
