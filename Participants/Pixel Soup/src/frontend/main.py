import arcade

from .gameconstants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from .views.mainview import MainView

import logging
import multiprocessing


def main() -> None:
    """Entry point of the game."""
    logging.basicConfig(level=logging.INFO)

    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    main_view = MainView()
    window.show_view(main_view)
    main_view.setup()
    arcade.run()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
