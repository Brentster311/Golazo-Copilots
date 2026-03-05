"""
BOB-001: Bob the stick figure — sits, stands up, and flies a kite.
A simple pygame animation.
"""

import sys
import math

try:
    import pygame
except ImportError:
    print("pygame is required. Install it with:  pip install pygame")
    sys.exit(1)

# ── Constants ────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 600, 500
FPS = 60
BG_COLOR = (173, 216, 230)  # light blue sky
GROUND_Y = 420
GROUND_COLOR = (34, 139, 34)  # green
BOB_COLOR = (20, 20, 20)
KITE_COLOR = (220, 40, 40)
KITE_TAIL_COLOR = (220, 100, 40)
STRING_COLOR = (80, 80, 80)
LINE_WIDTH = 4

# ── Animation timing (seconds) ──────────────────────────────────────────────
PHASE_SIT = 2.0        # hold sitting pose
PHASE_STAND = 2.0      # transition sit → stand
PHASE_RAISE_ARM = 1.0  # raise arm to hold kite string
PHASE_FLY_KITE = 4.0   # fly the kite
PHASE_LOWER_ARM = 1.0  # lower arm, kite drifts away
PHASE_SIT_DOWN = 2.0   # transition stand → sit
TOTAL_CYCLE = PHASE_SIT + PHASE_STAND + PHASE_RAISE_ARM + PHASE_FLY_KITE + PHASE_LOWER_ARM + PHASE_SIT_DOWN


def lerp(a, b, t):
    """Linear interpolation between a and b by factor t (0-1)."""
    return a + (b - a) * t


def lerp_pos(p1, p2, t):
    """Lerp between two (x, y) tuples."""
    return (lerp(p1[0], p2[0], t), lerp(p1[1], p2[1], t))


def ease_in_out(t):
    """Smooth ease-in-out (cubic)."""
    if t < 0.5:
        return 4 * t * t * t
    return 1 - (-2 * t + 2) ** 3 / 2


# ── Pose definitions ────────────────────────────────────────────────────────
# All positions relative to a base_x, base_y (Bob's hip center).
# Format: dict with head, neck, hip, left_knee, right_knee,
#          left_foot, right_foot, left_hand, right_hand, left_elbow, right_elbow

def sitting_pose(bx, by):
    """Bob sitting on the ground, legs stretched forward."""
    return {
        "head": (bx, by - 90),
        "neck": (bx, by - 65),
        "hip": (bx, by),
        # sitting: knees bent forward
        "left_knee": (bx - 25, by + 10),
        "right_knee": (bx + 25, by + 10),
        "left_foot": (bx - 55, by + 45),
        "right_foot": (bx + 15, by + 45),
        # feet (toes) — angled lines from ankle
        "left_toe": (bx - 70, by + 38),
        "right_toe": (bx + 30, by + 38),
        # arms resting
        "left_elbow": (bx - 30, by - 35),
        "right_elbow": (bx + 30, by - 35),
        "left_hand": (bx - 35, by - 5),
        "right_hand": (bx + 35, by - 5),
    }


def standing_pose(bx, by):
    """Bob standing upright."""
    return {
        "head": (bx, by - 130),
        "neck": (bx, by - 105),
        "hip": (bx, by - 40),
        "left_knee": (bx - 10, by - 20),
        "right_knee": (bx + 10, by - 20),
        "left_foot": (bx - 15, by),
        "right_foot": (bx + 15, by),
        # feet (toes)
        "left_toe": (bx - 30, by - 5),
        "right_toe": (bx + 30, by - 5),
        "left_elbow": (bx - 25, by - 75),
        "right_elbow": (bx + 25, by - 75),
        "left_hand": (bx - 25, by - 45),
        "right_hand": (bx + 25, by - 45),
    }


def kite_pose(bx, by):
    """Bob standing with right arm raised to hold kite string."""
    p = standing_pose(bx, by)
    p["right_elbow"] = (bx + 20, by - 110)
    p["right_hand"] = (bx + 30, by - 135)
    return p


def blend_pose(pose_a, pose_b, t):
    """Blend between two poses by factor t (0→pose_a, 1→pose_b)."""
    result = {}
    for key in pose_a:
        result[key] = lerp_pos(pose_a[key], pose_b[key], t)
    return result


# ── Drawing helpers ──────────────────────────────────────────────────────────

def draw_bob(surface, pose):
    """Draw Bob as a stick figure from a pose dict."""
    head_pos = (int(pose["head"][0]), int(pose["head"][1]))
    neck = pose["neck"]
    hip = pose["hip"]

    # Head (circle)
    pygame.draw.circle(surface, BOB_COLOR, head_pos, 18, LINE_WIDTH)

    # Spine (neck to hip)
    pygame.draw.line(surface, BOB_COLOR, _int2(neck), _int2(hip), LINE_WIDTH)

    # Left arm: neck → elbow → hand
    pygame.draw.line(surface, BOB_COLOR, _int2(neck), _int2(pose["left_elbow"]), LINE_WIDTH)
    pygame.draw.line(surface, BOB_COLOR, _int2(pose["left_elbow"]), _int2(pose["left_hand"]), LINE_WIDTH)

    # Right arm: neck → elbow → hand
    pygame.draw.line(surface, BOB_COLOR, _int2(neck), _int2(pose["right_elbow"]), LINE_WIDTH)
    pygame.draw.line(surface, BOB_COLOR, _int2(pose["right_elbow"]), _int2(pose["right_hand"]), LINE_WIDTH)

    # Left leg: hip → knee → foot
    pygame.draw.line(surface, BOB_COLOR, _int2(hip), _int2(pose["left_knee"]), LINE_WIDTH)
    pygame.draw.line(surface, BOB_COLOR, _int2(pose["left_knee"]), _int2(pose["left_foot"]), LINE_WIDTH)

    # Right leg: hip → knee → foot
    pygame.draw.line(surface, BOB_COLOR, _int2(hip), _int2(pose["right_knee"]), LINE_WIDTH)
    pygame.draw.line(surface, BOB_COLOR, _int2(pose["right_knee"]), _int2(pose["right_foot"]), LINE_WIDTH)

    # Feet (angled lines from ankle to toe)
    pygame.draw.line(surface, BOB_COLOR, _int2(pose["left_foot"]), _int2(pose["left_toe"]), LINE_WIDTH)
    pygame.draw.line(surface, BOB_COLOR, _int2(pose["right_foot"]), _int2(pose["right_toe"]), LINE_WIDTH)


def draw_kite(surface, hand_pos, t, kite_alpha):
    """Draw a kite attached to hand_pos. t is elapsed time for sway. kite_alpha is 0-1 opacity."""
    if kite_alpha <= 0:
        return

    # Kite position: above and to the right of the hand
    sway_x = math.sin(t * 1.8) * 30
    sway_y = math.cos(t * 2.3) * 15
    kite_cx = hand_pos[0] + 60 + sway_x
    kite_cy = hand_pos[1] - 120 + sway_y

    # String from hand to kite
    string_color = tuple(int(lerp(BG_COLOR[i], STRING_COLOR[i], kite_alpha)) for i in range(3))
    pygame.draw.line(surface, string_color, _int2(hand_pos), (int(kite_cx), int(kite_cy)), 2)

    # Kite diamond — short point at top, long tail point at bottom
    kite_size = 28
    kite_points = [
        (int(kite_cx), int(kite_cy - kite_size * 0.7)),   # top (short)
        (int(kite_cx + kite_size), int(kite_cy - kite_size * 0.1)),  # right
        (int(kite_cx), int(kite_cy + kite_size * 1.4)),   # bottom (long point)
        (int(kite_cx - kite_size), int(kite_cy - kite_size * 0.1)),  # left
    ]
    kite_color = tuple(int(lerp(BG_COLOR[i], KITE_COLOR[i], kite_alpha)) for i in range(3))
    pygame.draw.polygon(surface, kite_color, kite_points)
    pygame.draw.polygon(surface, tuple(max(0, c - 40) for c in kite_color), kite_points, 3)

    # Cross on kite
    pygame.draw.line(surface, tuple(max(0, c - 60) for c in kite_color),
                     kite_points[0], kite_points[2], 2)
    pygame.draw.line(surface, tuple(max(0, c - 60) for c in kite_color),
                     kite_points[3], kite_points[1], 2)

    # Tail
    tail_start = kite_points[2]
    tail_color = tuple(int(lerp(BG_COLOR[i], KITE_TAIL_COLOR[i], kite_alpha)) for i in range(3))
    for seg in range(4):
        seg_t = t * 2.5 + seg * 1.2
        dx = math.sin(seg_t) * (12 + seg * 4)
        dy = 15 + seg * 12
        tail_end = (int(tail_start[0] + dx), int(tail_start[1] + dy))
        pygame.draw.line(surface, tail_color, tail_start, tail_end, 2)
        tail_start = tail_end


def draw_ground(surface):
    """Draw the ground plane."""
    pygame.draw.rect(surface, GROUND_COLOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    # Grass line
    pygame.draw.line(surface, (20, 100, 20), (0, GROUND_Y), (WIDTH, GROUND_Y), 3)


def draw_clouds(surface, t):
    """Draw a couple of simple clouds drifting."""
    for i, (base_x, cy, speed) in enumerate([(100, 60, 15), (350, 90, 10), (500, 45, 20)]):
        cx = (base_x + t * speed) % (WIDTH + 120) - 60
        cloud_color = (240, 240, 250)
        for dx, dy, r in [(-15, 0, 18), (10, -5, 22), (30, 2, 16), (0, 10, 14)]:
            pygame.draw.circle(surface, cloud_color, (int(cx + dx), int(cy + dy)), r)


def draw_label(surface, font, text, x, y):
    """Draw centered text label."""
    rendered = font.render(text, True, (50, 50, 80))
    rect = rendered.get_rect(center=(x, y))
    surface.blit(rendered, rect)


def _int2(pos):
    """Convert float tuple to int tuple."""
    return (int(pos[0]), int(pos[1]))


# ── Main loop ────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bob's Kite Adventure")
    clock = pygame.time.Clock()

    try:
        font = pygame.font.SysFont("Arial", 20)
    except Exception:
        font = pygame.font.Font(None, 24)

    # Bob's base position (feet on ground)
    bob_x = WIDTH // 2 - 40
    bob_y = GROUND_Y

    # Pre-compute poses
    sit = sitting_pose(bob_x, bob_y)
    stand = standing_pose(bob_x, bob_y)
    kite = kite_pose(bob_x, bob_y)

    total_time = 0.0
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        total_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # ── Determine phase and interpolation ────────────────────────────
        cycle_t = total_time % TOTAL_CYCLE
        phase_label = ""
        kite_alpha = 0.0

        if cycle_t < PHASE_SIT:
            # Phase 1: Sitting
            pose = sit
            phase_label = "Bob is sitting..."
            kite_alpha = 0.0

        elif cycle_t < PHASE_SIT + PHASE_STAND:
            # Phase 2: Standing up
            raw_t = (cycle_t - PHASE_SIT) / PHASE_STAND
            t = ease_in_out(raw_t)
            pose = blend_pose(sit, stand, t)
            phase_label = "Bob stands up!"
            kite_alpha = 0.0

        elif cycle_t < PHASE_SIT + PHASE_STAND + PHASE_RAISE_ARM:
            # Phase 3: Raise arm for kite
            raw_t = (cycle_t - PHASE_SIT - PHASE_STAND) / PHASE_RAISE_ARM
            t = ease_in_out(raw_t)
            pose = blend_pose(stand, kite, t)
            kite_alpha = t  # kite fades in
            phase_label = "Time for a kite!"

        elif cycle_t < PHASE_SIT + PHASE_STAND + PHASE_RAISE_ARM + PHASE_FLY_KITE:
            # Phase 4: Flying the kite
            pose = kite
            kite_alpha = 1.0
            phase_label = "Bob flies a kite!"

        elif cycle_t < PHASE_SIT + PHASE_STAND + PHASE_RAISE_ARM + PHASE_FLY_KITE + PHASE_LOWER_ARM:
            # Phase 5: Lower arm, kite drifts away
            raw_t = (cycle_t - PHASE_SIT - PHASE_STAND - PHASE_RAISE_ARM - PHASE_FLY_KITE) / PHASE_LOWER_ARM
            t = ease_in_out(raw_t)
            pose = blend_pose(kite, stand, t)
            kite_alpha = 1.0 - t  # kite fades out
            phase_label = "Kite drifts away..."

        else:
            # Phase 6: Sitting back down
            raw_t = (cycle_t - PHASE_SIT - PHASE_STAND - PHASE_RAISE_ARM - PHASE_FLY_KITE - PHASE_LOWER_ARM) / PHASE_SIT_DOWN
            t = ease_in_out(raw_t)
            pose = blend_pose(stand, sit, t)
            phase_label = "Bob sits down..."
            kite_alpha = 0.0

        # ── Draw ─────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)
        draw_clouds(screen, total_time)
        draw_ground(screen)
        draw_bob(screen, pose)
        draw_kite(screen, pose["right_hand"], total_time, kite_alpha)
        draw_label(screen, font, phase_label, WIDTH // 2, HEIGHT - 30)

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
