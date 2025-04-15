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
base_rotation_speed = math.radians(30)  # degrees per second

# Ball
ball_pos = [WIDTH // 2, HEIGHT // 2 - 100]
ball_vel = [100, 0]

# Water area
WATER_LEVEL = HEIGHT // 2 + 100
WATER_DRAG = 0.8

# Easter egg counter
c_press_count = 0
rainbow_mode = False
rainbow_hue = 0

# Wind
wind = 0

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
rotation_speed = base_rotation_speed
running = True
while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                c_press_count += 1
                if c_press_count >= 10:
                    rainbow_mode = True
            if event.key == pygame.K_a:
                rotation_speed = -base_rotation_speed * 1.5
            if event.key == pygame.K_d:
                rotation_speed = base_rotation_speed * 1.5
        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_a, pygame.K_d):
                rotation_speed = base_rotation_speed

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        wind = -50
    elif keys[pygame.K_RIGHT]:
        wind = 50
    else:
        wind = 0

    # Update angle
    angle += rotation_speed * dt

    # Update velocity and position
    ball_vel[0] += wind * dt
    ball_vel[1] += g * dt

    if ball_pos[1] > WATER_LEVEL:
        ball_vel[0] *= WATER_DRAG
        ball_vel[1] *= WATER_DRAG

    ball_vel[0] *= friction
    ball_vel[1] *= friction
    ball_pos[0] += ball_vel[0] * dt
    ball_pos[1] += ball_vel[1] * dt

    # Collision with hexagon
    hexagon = get_hexagon((WIDTH // 2, HEIGHT // 2), hexagon_radius, angle)
    for i in range(6):
        p1 = hexagon[i]
        p2 = hexagon[(i + 1) % 6]

        edge = (p2[0] - p1[0], p2[1] - p1[1])
        edge_len = math.hypot(*edge)
        if edge_len == 0:
            continue
        edge_unit = (edge[0] / edge_len, edge[1] / edge_len)
        normal = (-edge_unit[1], edge_unit[0])

        rel = (ball_pos[0] - p1[0], ball_pos[1] - p1[1])
        dist = rel[0]*normal[0] + rel[1]*normal[1]

        proj_len = rel[0]*edge_unit[0] + rel[1]*edge_unit[1]
        if -BALL_RADIUS < dist < BALL_RADIUS and 0 <= proj_len <= edge_len:
            overlap = BALL_RADIUS - dist
            ball_pos[0] += normal[0] * overlap
            ball_pos[1] += normal[1] * overlap
            ball_vel = reflect_vector(ball_vel, normal)

    # Draw
    if rainbow_mode:
        rainbow_hue = (rainbow_hue + 60 * dt) % 360
        color = pygame.Color(0)
        color.hsva = (rainbow_hue, 100, 100, 100)
        screen.fill(color)
    else:
        screen.fill((10, 10, 30))

    pygame.draw.polygon(screen, (200, 200, 255), hexagon, 2)
    pygame.draw.rect(screen, (30, 30, 100), (0, WATER_LEVEL, WIDTH, HEIGHT - WATER_LEVEL))
    pygame.draw.circle(screen, (255, 50, 50), (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)
    pygame.display.flip()

pygame.quit()
sys.exit()

