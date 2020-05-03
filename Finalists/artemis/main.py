"""Run the actual game. This is the only file intended to be run directly."""
import arcade

from constants import BACKGROUND
from views import Menu


window = arcade.Window(title='Gem Matcher')
window.set_fullscreen(True)
arcade.set_background_color(BACKGROUND)
window.show_view(Menu())
window.set_vsync(True)
arcade.run()
