"""One-off tool for defining a polygon mask by clicking points on an image."""

import json
import pygame as pg

# Config
IMAGE_PATH = "miscellaneous/water_ripples/images/patagonia_lake.jpg"
OUTPUT_PATH = "miscellaneous/water_ripples/polygon_points.json"
WINDOW_WIDTH = 4000
WINDOW_HEIGHT = 2500
POINT_RADIUS = 5
POINT_COLOR = (255, 0, 0)
LINE_COLOR = (255, 255, 0)
PREVIEW_LINE_COLOR = (255, 255, 0, 128)
FONT_COLOR = (255, 255, 255)
BACKGROUND_COLOR = (0, 0, 0)


def save_points(points: list[tuple[int, int]], output_path: str) -> None:
    """Save polygon points to a JSON file, normalized to [0, 1]."""
    normalized = [
        (x / WINDOW_WIDTH, y / WINDOW_HEIGHT) for x, y in points
    ]
    with open(output_path, "w") as f:
        json.dump(normalized, f, indent=2)
    print(f"Saved {len(points)} points to {output_path}")


def main() -> None:
    pg.init()
    screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pg.display.set_caption("Click to define polygon — Enter to save, Z to undo, ESC to quit")
    font = pg.font.SysFont("monospace", 18)

    background = pg.image.load(IMAGE_PATH).convert()
    background = pg.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

    points: list[tuple[int, int]] = []
    running = True

    while running:
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_RETURN and len(points) >= 3:
                    save_points(points, OUTPUT_PATH)
                    running = False
                elif event.key == pg.K_z and points:
                    points.pop()
            elif event.type == pg.MOUSEBUTTONDOWN:
                points.append(mouse_pos)

        # Draw
        screen.blit(background, (0, 0))

        # Draw completed edges
        if len(points) >= 2:
            pg.draw.lines(screen, LINE_COLOR, False, points, 2)

        # Draw closing preview line from last point to mouse
        if len(points) >= 1:
            pg.draw.line(screen, PREVIEW_LINE_COLOR, points[-1], mouse_pos, 1)

        # Draw closing line preview from mouse back to first point
        if len(points) >= 2:
            pg.draw.line(screen, PREVIEW_LINE_COLOR, mouse_pos, points[0], 1)

        # Draw points
        for point in points:
            pg.draw.circle(screen, POINT_COLOR, point, POINT_RADIUS)

        # HUD
        instructions = [
            "Left click: add point",
            "Z: undo last point",
            "Enter: save & quit (min 3 points)",
            "ESC: quit without saving",
            f"Points: {len(points)}",
        ]
        for i, line in enumerate(instructions):
            text = font.render(line, True, FONT_COLOR)
            screen.blit(text, (10, 10 + i * 22))

        pg.display.flip()

    pg.quit()


main()