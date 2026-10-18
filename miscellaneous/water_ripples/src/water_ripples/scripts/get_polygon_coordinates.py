"""Script for drawing a polygon on the reference image by clicking points.

Left click adds a point, Z undoes the last point, Enter saves the polygon (at least three points) and
quits, and ESC quits without saving. Run it from the project root with:

    uv run python -m water_ripples.scripts.get_polygon_coordinates
"""

import logging
from pathlib import Path
from typing import Literal

import pygame as pg

from water_ripples.config_manager import ConfigManager
from water_ripples.polygons import save_polygon

logger = logging.getLogger(__name__)

PickerAction = Literal["continue", "save", "quit"]

_MINIMUM_POINTS = 3
_POINT_RADIUS = 5
_POINT_COLOR = (255, 0, 0)
_LINE_COLOR = (255, 255, 0)
_PREVIEW_LINE_COLOR = (255, 255, 0, 128)
_FONT_COLOR = (255, 255, 255)
_CAPTION = "Click to define polygon - Enter to save, Z to undo, ESC to quit"
_INSTRUCTIONS = [
    "Left click: add point",
    "Z: undo last point",
    f"Enter: save & quit (min {_MINIMUM_POINTS} points)",
    "ESC: quit without saving",
]


def handle_event(
    event: pg.event.Event,
    points: list[tuple[int, int]],
    mouse_pos: tuple[int, int],
) -> PickerAction:
    """Update the points for one event and say what the picker should do next.

    Args:
        event (pg.event.Event): The PyGame event to handle.
        points (list[tuple[int, int]]): The points drawn so far. Modified in place.
        mouse_pos (tuple[int, int]): The mouse position, used when a point is added.

    Returns:
        action (PickerAction): "save" to save and quit, "quit" to quit without saving, or
            "continue" to keep going.
    """
    if event.type == pg.QUIT:
        action: PickerAction = "quit"
    elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
        action = "quit"
    elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN and len(points) >= _MINIMUM_POINTS:
        action = "save"
    elif event.type == pg.KEYDOWN and event.key == pg.K_z and points:
        points.pop()
        action = "continue"
    elif event.type == pg.MOUSEBUTTONDOWN:
        points.append(mouse_pos)
        action = "continue"
    else:
        action = "continue"

    return action


def draw_picker(
    screen: pg.Surface,
    font: pg.font.Font,
    background: pg.Surface,
    points: list[tuple[int, int]],
    mouse_pos: tuple[int, int],
) -> None:
    """Draw the background, the polygon so far, the preview lines and the instructions.

    Args:
        screen (pg.Surface): The window surface to draw on.
        font (pg.font.Font): Font for the instructions.
        background (pg.Surface): The reference image, scaled to the window.
        points (list[tuple[int, int]]): The points drawn so far.
        mouse_pos (tuple[int, int]): The current mouse position, for the preview lines.
    """
    screen.blit(background, (0, 0))

    if len(points) >= 2:
        pg.draw.lines(screen, _LINE_COLOR, False, points, 2)

    if len(points) >= 1:
        pg.draw.line(screen, _PREVIEW_LINE_COLOR, points[-1], mouse_pos, 1)

    if len(points) >= 2:
        pg.draw.line(screen, _PREVIEW_LINE_COLOR, mouse_pos, points[0], 1)

    for point in points:
        pg.draw.circle(screen, _POINT_COLOR, point, _POINT_RADIUS)

    point_count = len(points)
    lines = [*_INSTRUCTIONS, f"Points: {point_count}"]
    for line_number, line in enumerate(lines):
        text = font.render(line, True, _FONT_COLOR)
        screen.blit(text, (10, 10 + line_number * 22))


def run_picker(
    image_path: Path,
    polygon_path: Path,
    reference_width: int,
    reference_height: int,
) -> bool:
    """Let the user click a polygon on the image, and save it when they press Enter.

    Args:
        image_path (str): The image to draw on.
        polygon_path (str): Where to save the normalized polygon JSON.
        reference_width (int): Width of the window, which is also the reference size.
        reference_height (int): Height of the window, which is also the reference size.

    Returns:
        saved (bool): True if the polygon was saved, False if the user quit without saving.
    """
    pg.init()
    screen = pg.display.set_mode((reference_width, reference_height))
    pg.display.set_caption(_CAPTION)
    font = pg.font.Font(None, 28)

    background = pg.image.load(image_path).convert()
    background = pg.transform.scale(background, (reference_width, reference_height))

    points: list[tuple[int, int]] = []
    saved = False
    running = True

    while running:
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            action = handle_event(event=event, points=points, mouse_pos=mouse_pos)

            if action == "save":
                save_polygon(
                    points=points,
                    polygon_path=polygon_path,
                    reference_width=reference_width,
                    reference_height=reference_height,
                )
                saved = True
                running = False
            elif action == "quit":
                running = False

        draw_picker(
            screen=screen,
            font=font,
            background=background,
            points=points,
            mouse_pos=mouse_pos,
        )

        pg.display.flip()

    pg.quit()

    return saved


def main() -> None:
    """Load the configuration and run the picker on the configured image."""
    logging.basicConfig(level=logging.INFO)

    config = ConfigManager().load_config_file()
    image_config = config.image
    saved = run_picker(
        image_path=image_config.image_path,
        polygon_path=image_config.polygon_path,
        reference_width=image_config.reference_width,
        reference_height=image_config.reference_height,
    )

    if saved:
        logger.info(f"Saved polygon to {image_config.polygon_path}")
    else:
        logger.info("Quit without saving.")


if __name__ == "__main__":
    main()
