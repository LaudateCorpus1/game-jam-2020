"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Triple Dungeon!!!"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 2

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5


# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.wall_list = None
        self.floor_list = None
        self.player_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # Our physics engine
        self.physics_engine = None

        #list to keep track of keypresses
        self.prev_keypress = []

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        arcade.set_background_color(arcade.csscolor.BLACK)

    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        # Create the Sprite lists
        self.wall_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        image_source = "images/monsters/skeleton.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_sprite.scale = 4
        self.player_list.append(self.player_sprite)

        # Create the floor
        # This shows using a loop to place multiple sprites horizontally and vertically
        for y in range(0, 1250, 63 * TILE_SCALING):
            for x in range(0, 1250, 63 * TILE_SCALING):
                floor = arcade.Sprite("images/tiles/floor_tile.png", TILE_SCALING)
                floor.center_x = x
                floor.center_y = y
                self.floor_list.append(floor)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.floor_list.draw()
        self.player_list.draw()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            self.prev_keypress.append(key)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
            self.prev_keypress.append(key)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.prev_keypress.append(key)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.prev_keypress.append(key)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
            self.prev_keypress.remove(key)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
            self.prev_keypress.remove(key)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
            self.prev_keypress.remove(key)
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0
            self.prev_keypress.remove(key)

        if self.prev_keypress:
            self.on_key_press(self.prev_keypress.pop(0), '')

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Move the player with the physics engine
        self.physics_engine.update()

                # --- Manage Scrolling ---

        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
