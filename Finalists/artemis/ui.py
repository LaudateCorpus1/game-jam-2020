"""Various UI elements."""
from PIL import Image, ImageDraw, ImageFont
import typing
import arcade

from constants import ASSETS, FONT, HEIGHT, WIDTH
from sound import play_sound_effect


number = typing.Union[int, float]


class IconButton:
    """A button, displayed with an icon."""

    def __init__(self, view: arcade.View, x: number, y: number, image: str,
                 fun: typing.Callable, size: int = 64, tooltip: str = None):
        """Load textures and record parameters."""
        self.view = view
        self.state = 'normal'
        self.tooltip_text = tooltip
        if not tooltip:
            self.tooltip_text = image.replace('_', ' ').title()
        self.tooltip_texture = self.create_tooltip()
        self.icon_texture = self.load_texture(image, size // 2)
        self.textures = {}
        for state in ('normal', 'pressed', 'hover'):
            self.textures[state] = self.load_texture('button_' + state, size)
        self.fun = fun
        self.center_x = x
        self.center_y = y
        self.size = size
        self.sound = arcade.Sound(':resources:/sounds/jump1.wav')

    def load_texture(self, file: str, size: int) -> arcade.Texture:
        """Load a texture from a file. Arcade wasn't resizing nicely."""
        im = Image.open(f'{ASSETS}{file}.png').resize((size, size))
        return arcade.Texture(file, im)

    def create_tooltip(self) -> arcade.Texture:
        """Create an arcade texture for the tooltip."""
        padding = 5
        font = ImageFont.truetype(FONT.format(type='ri'), 20)
        text_width, text_height = font.getsize(self.tooltip_text)
        width = text_width + padding * 2
        height = text_height + padding * 2
        im = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(im)
        draw.text((padding, padding), self.tooltip_text, (0, 0, 0), font)
        return arcade.Texture(str(self.tooltip_text), im)

    def on_draw(self):
        """Draw textures."""
        self.textures[self.state].draw_scaled(self.center_x, self.center_y)
        self.icon_texture.draw_scaled(self.center_x, self.center_y)
        if self.state == 'hover':
            x = self.right + self.tooltip_texture.width / 2 - 15
            y = self.bottom - self.tooltip_texture.height / 2 + 15
            _left, right, _top, _bottom = arcade.get_viewport()
            x = min(x, right - self.tooltip_texture.width / 2)
            self.tooltip_texture.draw_scaled(x, y)
            if self not in self.view.on_top:
                self.view.on_top.append(self)
        elif self in self.view.on_top:
            self.view.on_top.remove(self)

    @property
    def left(self) -> float:
        """Get the left of the button."""
        return self.center_x - self.size / 2

    @property
    def right(self) -> float:
        """Get the right of the button."""
        return self.center_x + self.size / 2

    @property
    def top(self) -> float:
        """Get the top of the button."""
        return self.center_y + self.size / 2

    @property
    def bottom(self) -> float:
        """Get the bottom of the button."""
        return self.center_y - self.size / 2

    def on_click(self, _x: float, _y: float):
        """Play sound effect and set state."""
        play_sound_effect('mouseclick')
        self.state = 'pressed'

    def touching(self, x: float, y: float) -> bool:
        """Check if the mouse is touching the button."""
        x += arcade.get_viewport()[0]
        return self.left <= x <= self.right and self.bottom <= y <= self.top

    def on_release(self, _x: float, _y: float):
        """Play sound effect, update state and run callback."""
        play_sound_effect('mouserelease')
        self.fun()
        self.state = 'normal'

    def on_mouse_press(self, x: float, y: float, _button: int,
                       _modifiers: int):
        """Check if a mouse press is on the button."""
        if self.touching(x, y):
            self.on_click(x, y)

    def on_mouse_motion(self, x: float, y: float, _dx: int, _dy: int):
        """Check if mouse motion is hovering on the button."""
        if self.touching(x, y):
            if self.state != 'pressed':
                self.state = 'hover'
        else:
            self.state = 'normal'

    def on_mouse_release(self, x: int, y: int, _button: int, _modifiers: int):
        """Check if a mouse release is a click on the button."""
        if self.state == 'pressed':
            self.on_release(x, y)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      _buttons: int, _modifiers: int):
        """Don't do anything."""


class Slider(IconButton):
    """A horizontal slider."""

    def __init__(self, view: arcade.View, x: number, y: number,
                 initial: number, on_change: typing.Callable,
                 width: int = WIDTH // 3):
        """Load textures and record parameters."""
        self.view = view
        self.state = 'normal'
        self.textures = {}
        for state in ('normal', 'pressed', 'hover'):
            self.textures[state] = self.load_texture(
                'button_' + state, 32
            )
        self.fun = on_change
        self.center_x = x
        self.center_y = y
        self.position = initial * width
        self.width = width
        self.size = 32

    @property
    def value(self) -> float:
        """Get the value selected by the user (0 to 1)."""
        return self.position / self.width

    def on_draw(self):
        """Draw textures."""
        if self.position > self.width:
            self.position = self.width
        elif self.position < 0:
            self.position = 0
        arcade.draw_line(
            self.left, self.center_y, self.right, self.center_y,
            (255, 255, 255), 10
        )
        self.textures[self.state].draw_scaled(
            self.left + self.position, self.center_y
        )

    @property
    def left(self) -> float:
        """Get the left of the slider."""
        return self.center_x - self.width / 2

    @property
    def right(self) -> float:
        """Get the right of the slider."""
        return self.center_x + self.width / 2

    def update_position(self, x: float):
        """Update the position of our button based on mouse position."""
        self.position = min(max((0, x - self.left)), self.width)

    def on_click(self, x: float, y: float):
        """Update position and change texture."""
        self.update_position(x)
        super().on_click(x, y)

    def on_drag(self, x: float, _y: float):
        """Update position."""
        self.update_position(x)

    def on_release(self, x: float, y: float):
        """Update position, change texture and execute callback."""
        self.update_position(x)
        super().on_release(x, y)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      _buttons: int, _modifiers: int):
        """Check if a mouse release is a click on the button."""
        if self.touching(x, y) and self.state == 'pressed':
            self.state = 'pressed'
            self.on_drag(x, y)
        elif self.bottom < y < self.top and self.state == 'pressed':
            if x < self.left:
                self.on_drag(self.left, y)
            if x > self.right:
                self.on_drag(self.right, y)


class Achievement(IconButton):
    """The display for an achievement."""

    def __init__(self, view: arcade.View, x: number, y: number, typ: int,
                 level: int, name: str, description: str, achieved: bool,
                 size: int = 64):
        """Load textures and store parameters."""
        self.typ = typ
        self.level = level
        self.setup(view, x, y, name, description, achieved, size)

    def setup(self, view: arcade.View, x: number, y: number, name: str,
              description: str, achieved: bool, size: int):
        """Save parameters and load textures common with Awards."""
        self.view = view
        self.state = 'normal'
        self.size = size
        self.name = name
        self.desc = description
        self.tooltip_texture = self.create_tooltip()
        self.center_x = x
        self.center_y = y
        self.alpha = 255 if achieved else 100
        self.achieved = achieved
        self.load_textures()

    def load_textures(self):
        """Load background and icon texture."""
        self.icon_texture = self.load_texture(
            f'achievement_type_{self.typ}', self.size // 2
        )
        self.background_texture = self.load_texture(
            f'achievement_level_{self.level}', self.size
        )

    def create_tooltip(self) -> arcade.Texture:
        """Create an arcade texture for the tooltip."""
        gap = 5
        name_font = ImageFont.truetype(FONT.format(type='r'), 20)
        desc_font = ImageFont.truetype(FONT.format(type='ri'), 15)
        name_width, name_height = name_font.getsize(self.name)
        desc_width, desc_height = desc_font.getsize(self.desc)
        width = max(name_width, desc_width) + gap * 2
        height = name_height + gap * 3 + desc_height
        im = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(im)
        draw.text((gap, gap), self.name, (0, 0, 0), name_font)
        draw.text(
            (gap, name_height + gap * 2), self.desc, (0, 0, 0), desc_font
        )
        return arcade.Texture(self.name + '\n' + self.desc, im)

    def on_draw(self):
        """Draw the relevant textures."""
        self.background_texture.draw_scaled(
            self.center_x, self.center_y, alpha=self.alpha
        )
        self.icon_texture.draw_scaled(
            self.center_x, self.center_y, alpha=self.alpha
        )
        if self.state == 'hover':
            x = self.right + self.tooltip_texture.width / 2 - 15
            y = self.bottom - self.tooltip_texture.height / 2 + 15
            self.tooltip_texture.draw_scaled(x, y)
            if self not in self.view.on_top:
                self.view.on_top.append(self)
        elif self in self.view.on_top:
            self.view.on_top.remove(self)

    def on_mouse_press(self, _x: float, _y: float, _button: int,
                       _modifiers: int):
        """Don't do anything since it isn't actually a button."""

    def on_mouse_release(self, _x: float, _y: float, _button: int,
                         _modifiers: int):
        """Don't do anything since it isn't actually a button."""


class Award(Achievement):
    """The display for an award."""

    def __init__(self, view: arcade.View, x: number, y: number, typ: int,
                 name: str, description: str, achieved: bool, size: int = 64):
        """Load textures and store parameters."""
        self.typ = typ
        self.achieved = achieved
        if not achieved:
            name = '???'
            description = ''
        self.setup(view, x, y, name, description, achieved, size)

    def load_textures(self):
        """Load background and icon texture."""
        visible = 'visible' if self.achieved else 'hidden'
        self.icon_texture = self.load_texture(
            f'award_{self.typ}_{visible}', self.size // 2
        )
        self.background_texture = self.load_texture('award', self.size)


class ViewButton(IconButton):
    """An icon button for switching views."""

    def __init__(self, view: arcade.View, x: number, y: number, image: str,
                 switch_to: typing.Type[arcade.View], size: int = 64):
        """Load textures and store parameters."""
        self.switch_to = switch_to
        super().__init__(view, x, y, image, self.switch)

    def switch(self):
        """Switch views."""
        self.view.window.show_view(self.switch_to())


class View(arcade.View):
    """Base class for views."""

    reset_viewport = True

    def __init__(self):
        """Reset viewport, create button list and start mouse hide timer."""
        super().__init__()
        if type(self).reset_viewport:
            arcade.set_viewport(0, WIDTH, 0, HEIGHT)
        self.buttons = []
        self.on_top = []
        self.hide_mouse_after = 1

    def on_update(self, td: float):
        """Hide mouse if ready."""
        self.hide_mouse_after -= td
        if self.hide_mouse_after < 0:
            visible = False
            for button in self.buttons:
                if button.state != 'normal':
                    visible = True
                    break
            self.window.set_mouse_visible(visible)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """Check motion with buttons and unhide mouse."""
        self.hide_mouse_after = 1
        self.window.set_mouse_visible(True)
        for button in self.buttons:
            button.on_mouse_motion(x, y, dx, dy)

    def on_draw(self, start_render: bool = True):
        """Draw buttons."""
        if start_render:
            arcade.start_render()
        for button in self.buttons:
            button.on_draw()
        for button in self.on_top:
            button.on_draw()

    def on_mouse_press(self, x: float, y: float, button_id: int,
                       modifiers: int):
        """Check mouse press with buttons."""
        for button in self.buttons:
            button.on_mouse_press(x, y, button_id, modifiers)

    def on_mouse_release(self, x: float, y: float, button_id: int,
                         modifiers: int):
        """Check mouse release with buttons."""
        for button in self.buttons:
            button.on_mouse_release(x, y, button_id, modifiers)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float,
                      buttons: int, modifiers: int):
        """Check mouse drag with buttons."""
        for button in self.buttons:
            button.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
