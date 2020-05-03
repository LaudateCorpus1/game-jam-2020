import math
import time
from typing import Optional

import arcade

from triple_vision.utils import get_change_vector, is_in_radius_positions
from triple_vision.entities.entities import Entity
from triple_vision.sound import SoundManager

class MovingSprite(arcade.Sprite):
    def __init__(self, moving_speed, rotate=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.speed = moving_speed
        self.speed_multiplier = 1
        self.target = None
        self.rotate = rotate

    def is_moving(self) -> bool:
        return any((self.change_x, self.change_y))

    def calc_change_vector(self, x: float, y: float) -> None:
        self.change_x, self.change_y, angle = get_change_vector(
            start_position=self.position,
            destination_position=(x, y),
            speed_multiplier=self.speed * self.speed_multiplier,
        )

        if self.rotate:
            # Angle the sprite
            self.angle = math.degrees(angle)

    def move_to(self, x: float, y: float, *, set_target: bool = True) -> None:
        """
        Move the MovingSprite into a given point on the screen.

        :param set_target: Represents if we want to set the point as a target
                           (the sprite will stop after reaching it)
        :param x: x coordinate for the sprite to move into
        :param y: y coordinate for the sprite to move into
        """
        self.calc_change_vector(x, y)

        if set_target:
            self.target = (x, y)

    def move_to_sprite(self, sprite: arcade.Sprite, *, set_target: bool = True) -> None:
        self.move_to(sprite.center_x, sprite.center_y, set_target=set_target)

    def move_to_angle(self, angle: int, *, rotate: bool = False) -> None:
        """
        Move in direction of angle.
        :param angle: angle in degrees to which to move the sprite (90 means to move sprite up)
        :param rotate: should we rotate the sprite around it's center to align it to the new
                       direction. Useful for example projectiles.
        """
        if rotate:
            self.angle = angle

        radians_angle = math.radians(angle)

        # Taking into account the angle, calculate our change_x and change_y.
        self.change_x = math.cos(radians_angle) * self.speed
        self.change_y = math.sin(radians_angle) * self.speed

    def force_moving_sprite_on_update(self, delta_time: float) -> None:
        """
        Another name for on_update
        For easier calling in case of heavy polymorphism
        """
        self._reached_target_check()
        self.update_(delta_time)

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self._reached_target_check()
        self.update_(delta_time)

    def _reached_target_check(self):
        if self.target is not None:
            self.calc_change_vector(*self.target)

            if is_in_radius_positions(self.position, self.target, 4):
                self.change_x = 0
                self.change_y = 0
                self.target = None

    def update_(self, delta_time):
        """
        Update method that works with slow-down.
        """
        relative_speed = delta_time * 60
        self.position = [
            self._position[0] + self.change_x * relative_speed,
            self._position[1] + self.change_y * relative_speed,
        ]
        self.angle += self.change_angle * relative_speed


class TemporarySprite(arcade.Sprite):
    def __init__(self, lifetime: Optional[int], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.lifetime = lifetime
        self._passed_time = 0.0
        self.created_at = time.time()

    def on_update(self, delta_time: float):
        self._passed_time += delta_time
        if self.lifetime and self._passed_time > self.lifetime:
            self.kill()
        super().on_update(delta_time)


class TextIndicator(TemporarySprite, MovingSprite):
    def __init__(self, text, start_x: int, start_y: int, color=(255, 255, 255)):
        super().__init__(
            lifetime=1,
            moving_speed=1,
            center_x=start_x,
            center_y=start_y,
            rotate=False
        )
        temp_text = arcade.draw_text(text, start_x, start_y, arcade.color.WHITE)
        self.texture = temp_text.texture
        self.color = color
        self.move_to(start_x, start_y + 10, set_target=False)


class ManaBar(arcade.Sprite):
    def __init__(
        self,
        view,
        fill_part_filename: str,
        fill_part_width: float,
        *args,
        max_fillers: int = 10,
        is_filled: bool = True,
        auto_filling_speed: Optional[float] = None,
        scale: float = 1,
        **kwargs
    ) -> None:

        super().__init__(*args, scale=scale, **kwargs)
        self.view = view
        self.fill_part_filename = fill_part_filename
        self.fill_part_width = fill_part_width * scale
        self.max_fillers = max_fillers
        self.fill_part_list = arcade.SpriteList()
        self.auto_filling_speed = auto_filling_speed
        if not is_filled:
            return

        for i in range(max_fillers):
            self.fill_part_list.append(
                arcade.Sprite(
                    fill_part_filename,
                    center_x=self.center_x + (self.fill_part_width - self.width) / 2
                    + self.fill_part_width * i,
                    center_y=self.center_y,
                    scale=scale,
                )
            )
        self.prev_viewport = (
            self.view.camera.viewport_left,
            self.view.camera.viewport_bottom,
        )
        self.waited_time = 0

    def __len__(self):
        return len(self.fill_part_list)

    def remove_filling_part(self):
        if len(self.fill_part_list) == 0:
            return
        self.fill_part_list.pop()

    def clear(self, amount):
        for _ in range(amount):
            self.remove_filling_part()

    def add_filling_part(self):
        if len(self.fill_part_list) < self.max_fillers:
            self.fill_part_list.append(
                arcade.Sprite(
                    self.fill_part_filename,
                    center_x=self.center_x + (self.fill_part_width - self.width) / 2
                    + self.fill_part_width * len(self.fill_part_list),
                    center_y=self.center_y,
                )
            )

    def on_update(self, delta_time: float = 1 / 60):
        self.waited_time += delta_time
        if self.auto_filling_speed is not None and self.waited_time >= self.auto_filling_speed:
            self.add_filling_part()
            self.waited_time = 0

        viewport = (self.view.camera.viewport_left, self.view.camera.viewport_bottom)
        if self.prev_viewport != viewport:
            viewport_change = viewport[0] - self.prev_viewport[0], viewport[1] - self.prev_viewport[1]
            self.center_x += viewport_change[0]
            self.center_y += viewport_change[1]
            for fill_part in self.fill_part_list:
                fill_part.center_x += viewport_change[0]
                fill_part.center_y += viewport_change[1]

            self.prev_viewport = viewport

        super().update()
        self.fill_part_list.on_update(delta_time)

    def draw(self):
        self.fill_part_list.draw()
        super().draw()


class PotionEffect:
    def __init__(self, heal=0.0, speed=0.0, strength=0.0, resistance=0.0):
        self.heal = heal
        self.speed = speed
        self.strength = strength
        self.resistance = resistance


class Potion(Entity):
    def __init__(self, ctx, player, effect: PotionEffect, duration: float = None, *args, **kwargs):
        super().__init__(ctx, *args, **kwargs)
        self.player = player
        self.effect = effect
        self.duration = duration
        self.wait_time = 0.0
        self._effect = effect

    def collected(self):
        self.player.attack_multiplier += self.effect.strength
        self.player.hp += self.effect.heal
        if self.player.hp >= self.player.MAX_HP:
            self.player.hp = self.player.MAX_HP
        self.player.speed_multiplier += self.effect.speed
        self.player.resistance += self.effect.resistance

        start_y = self.center_y
        for attribute in self._effect.__dict__.keys():
            value = self._effect.__getattribute__(attribute)
            if value > 0:
                if value % 1 == 0:
                    msg = f"+{value} {attribute}"
                else:
                    percentage = value * 100
                    msg = f"+{int(percentage)}% {attribute}"

                self.ctx.create_text_indicator(
                    msg,
                    (self.center_x, start_y),
                    color=(0, 255, 0)
                )
                start_y += 20

        SoundManager.add_sound("pickup_0.wav")
        SoundManager.play_sound("pickup_0.wav")

        if self.duration is None:
            self.kill()

    def on_update(self, delta_time: float = 1/60):
        if self.duration is None:
            return

        self.wait_time += delta_time

        if self.wait_time > self.duration:
            self.player.reset_stats()

