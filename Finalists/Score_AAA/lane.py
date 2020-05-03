import arcade
from entities import Character, Obstacle, Background
from enum import Enum


class EnumAction(Enum):
    miss = 0
    ok = 1
    super = 5
    perfect = 10


class Lane:
    """
    Initialise and generate most objects in one of the three lanes.
    """

    # init a lane with char/floor/physics engine/
    def __init__(
        self,
        tier: int,
        scale: int,
        SCREEN_HEIGHT: int,
        SCREEN_WIDTH: int,
        sprite_path: str,
        run_textures: list,
        pattern_texture: dict,
    ):
        """

        :param tier: What tier of the screen the lane should be.
        :param run_textures: A list of textures for running animation (only Q atm)
        """
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.tier = tier

        self.char = Character(
            sprite_path,
            SCREEN_HEIGHT - (SCREEN_HEIGHT // 3) * tier + 20,
            run_textures,
            pattern_texture,
        )
        self.char.center_x = SCREEN_WIDTH // 10
        self.char.scale = scale

        self.floor = arcade.Sprite("./ressources/Floor_Tempo.png")
        self.floor.center_y = SCREEN_HEIGHT - (SCREEN_HEIGHT // 3) * tier + 5
        floor_list = arcade.SpriteList()
        floor_list.append(self.floor)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.char, floor_list)
        self.valid_zone = self.generate_valid_zone()
        self.difficulty = 6

    def generate_obstacle(self, sprite_path: str) -> arcade.Sprite:
        """
        Used to generate an obstacle on the lane.
        """

        obstacle = Obstacle(sprite_path)
        obstacle.center_x = self.SCREEN_WIDTH
        obstacle.center_y = (
            self.SCREEN_HEIGHT - (self.SCREEN_HEIGHT // 3) * self.tier + 40
        )
        obstacle.scale = 0.8
        obstacle.change_x = -self.difficulty
        return obstacle

    def generate_valid_zone(self) -> arcade.Sprite:
        """
        Generate a sprite in front of the character,
        to detect correct input when an obstacle arrive.
        """
        valid_zone = arcade.Sprite("./ressources/Lane_Valid_Zone.png")
        valid_zone.center_x = (self.SCREEN_WIDTH // 10) * 2
        valid_zone.center_y = (
            self.SCREEN_HEIGHT - (self.SCREEN_HEIGHT // 3) * self.tier + 90
        )
        valid_zone.color = (0, 0, 0)  # To visualise if drawn
        return valid_zone

    def action(self, obstacle_list: arcade.SpriteList) -> EnumAction:
        """
        Called when a button is pressed, Jump and check if an obstacle is in the valid zone.
        """

        result = EnumAction.miss
        if self.physics_engine.can_jump(5):
            for collision in arcade.check_for_collision_with_list(
                self.valid_zone, obstacle_list
            ):
                collision.hit = True
                if (
                    self.valid_zone.center_x - 10
                    < collision.center_x
                    < self.valid_zone.center_x + 10
                ):
                    result = EnumAction.perfect
                elif (
                    collision.right < self.valid_zone.right
                    and collision.left > self.valid_zone.left
                ):
                    result = EnumAction.super
                else:
                    result = EnumAction.ok
            self.physics_engine.jump(6)
        return result

    def generate_background(self, sprite_path: str, speed: int, offset: int) -> list:
        """
        Generate background sprite on the lane.
        :param sprite_path: The path to the sprite. Sprite must be the size of the Screen.
        :param speed: The scrolling speed.
        :param offset: Magic Number :c to place them 'right'. 107 for Q, -93 for W.
        """
        # offset 107 for Q
        result = []
        background = Background(sprite_path, self.SCREEN_WIDTH)
        background.center_y = (
            self.SCREEN_HEIGHT - (self.SCREEN_HEIGHT // 3) * self.tier + offset
        )
        background.center_x = self.SCREEN_WIDTH // 2
        background.change_x = -speed
        result.append(background)

        background = Background(sprite_path, self.SCREEN_WIDTH)
        background.center_y = (
            self.SCREEN_HEIGHT - (self.SCREEN_HEIGHT // 3) * self.tier + offset
        )
        background.center_x = self.SCREEN_WIDTH + self.SCREEN_WIDTH // 2
        background.change_x = -speed
        result.append(background)
        return result
