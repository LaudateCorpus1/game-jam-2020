import arcade
from frost.client import Status

from triple_vision import Settings as s
from triple_vision.networking import client, get_status
from triple_vision.text_input import TextInput
from triple_vision.views.auth_failure import AuthenticationFailure
from triple_vision.views.main_view import MainView


class LoginButton(arcade.TextButton):

    def __init__(self, view, *args, **kwargs) -> None:
        super().__init__(text='', *args, **kwargs)
        self.view = view

        self.pressed = False

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.view.login()
            self.pressed = False


class RegisterButton(arcade.TextButton):

    def __init__(self, view, *args, **kwargs) -> None:
        super().__init__(text='', *args, **kwargs)
        self.view = view

        self.pressed = False

    def on_press(self):
        self.pressed = True

    def on_release(self):
        if self.pressed:
            self.view.register()
            self.pressed = False


class AuthTextInput(TextInput):

    def __init__(self, view, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.view = view

    def on_enter(self, text) -> None:
        if isinstance(self.view, LoginView):
            self.view.login()

        elif isinstance(self.view, RegisterView):
            self.view.register()

        else:
            raise TypeError('View should be an instance of LoginView or RegisterView.')


class AuthView(arcade.View):

    def __init__(self, view_text) -> None:
        super().__init__()

        self.username_text = None
        self.password_text = None

        self.username = None
        self.password = None

        self.game_title = None
        self.view_text = None
        self.view_raw_text = view_text

        self.login_button = None
        self.register_button = None

        self.background = arcade.load_texture('assets/background.png')

    def login(self) -> None:
        pass

    def register(self) -> None:
        pass

    def on_show(self) -> None:
        self.username_text = arcade.draw_text(
            text='Username:',
            start_x=s.WINDOW_SIZE[0] / 4 - 120,
            start_y=s.WINDOW_SIZE[1] / 2 + 40,
            color=arcade.color.WHITE,
            font_size=18,
            anchor_y='center'
        )
        self.password_text = arcade.draw_text(
            text='Password:',
            start_x=s.WINDOW_SIZE[0] / 4 - 120,
            start_y=s.WINDOW_SIZE[1] / 2 - 40,
            color=arcade.color.WHITE,
            font_size=18,
            anchor_y='center'
        )

        self.username = AuthTextInput(
            self,
            center_x=s.WINDOW_SIZE[0] / 2,
            center_y=s.WINDOW_SIZE[1] / 2 + 40,
            width=s.WINDOW_SIZE[0] / 2,
            height=36,
            font_size=18,
            border_width=5
        )
        self.password = AuthTextInput(
            self,
            center_x=s.WINDOW_SIZE[0] / 2,
            center_y=s.WINDOW_SIZE[1] / 2 - 40,
            width=s.WINDOW_SIZE[0] / 2,
            height=36,
            font_size=18,
            border_width=5
        )

        self.game_title = arcade.load_texture(
            'assets/title.png'
        )
        self.view_text = arcade.draw_text(
            text=self.view_raw_text,
            start_x=s.WINDOW_SIZE[0] / 2,
            start_y=s.WINDOW_SIZE[1] / 4 * 3,
            color=arcade.color.WHITE,
            font_size=32,
            align='center',
            anchor_x='center',
            anchor_y='center'
        )

        login_button_theme = arcade.Theme()
        login_button_theme.add_button_textures(
            clicked='assets/buttons/login_pressed.png',
            normal='assets/buttons/login_released.png'
        )

        register_button_theme = arcade.Theme()
        register_button_theme.add_button_textures(
            clicked='assets/buttons/register_pressed.png',
            normal='assets/buttons/register_released.png'
        )

        self.login_button = LoginButton(
            self,
            center_x=s.WINDOW_SIZE[0] / 2 + 60,
            center_y=s.WINDOW_SIZE[1] / 2 - 120,
            width=100,
            height=60,
            theme=login_button_theme
        )
        self.register_button = RegisterButton(
            self,
            center_x=s.WINDOW_SIZE[0] / 2 - 60,
            center_y=s.WINDOW_SIZE[1] / 2 - 120,
            width=100,
            height=60,
            theme=register_button_theme
        )

        self.window.button_list.extend([
            self.login_button,
            self.register_button
        ])

    def on_key_press(self, key, modifiers) -> None:
        self.username.process_key_press(key, modifiers)
        self.password.process_key_press(key, modifiers)

    def on_key_release(self, key, modifiers) -> None:
        self.username.process_key_release(key, modifiers)
        self.password.process_key_release(key, modifiers)

    def on_mouse_press(self, x, y, key, modifiers) -> None:
        self.username.process_mouse_press(x, y, key, modifiers)
        self.password.process_mouse_press(x, y, key, modifiers)

    def on_draw(self) -> None:
        arcade.start_render()

        arcade.draw_lrwh_rectangle_textured(
            bottom_left_x=0,
            bottom_left_y=0,
            width=s.WINDOW_SIZE[0],
            height=s.WINDOW_SIZE[1],
            texture=self.background
        )

        arcade.draw_lrwh_rectangle_textured(
            bottom_left_x=s.WINDOW_SIZE[0] / 2 - 449,
            bottom_left_y=s.WINDOW_SIZE[1] / 8 * 7 - 200,
            width=898,
            height=400,
            texture=self.game_title
        )

        self.username_text.draw()
        self.password_text.draw()

        self.username.draw()
        self.password.draw()

        self.view_text.draw()

        self.login_button.draw()
        self.register_button.draw()

    def on_update(self, delta_time: float = 1/60) -> None:
        self.username.on_update(delta_time)
        self.password.on_update(delta_time)


class LoginView(AuthView):

    def __init__(self) -> None:
        super().__init__('Login')

    def login(self) -> None:
        self.window.button_list.clear()

        client.login(self.username.text, self.password.text)
        status = get_status('login')

        if status == Status.SUCCESS:
            self.window.show_view(MainView())
        else:
            self.window.show_view(AuthenticationFailure(self, status))

    def register(self) -> None:
        self.window.button_list.clear()
        self.window.show_view(RegisterView())

    def on_show(self) -> None:
        super().on_show()

        self.login_button.center_x = s.WINDOW_SIZE[0] / 2 + 60
        self.register_button.center_x = s.WINDOW_SIZE[0] / 2 - 60


class RegisterView(AuthView):

    def __init__(self) -> None:
        super().__init__('Register')

    def login(self) -> None:
        self.window.button_list.clear()
        self.window.show_view(LoginView())

    def register(self) -> None:
        self.window.button_list.clear()

        client.register(self.username.text, self.password.text)
        status = get_status('register')

        if status == Status.SUCCESS:
            self.window.show_view(LoginView())
        else:
            self.window.show_view(AuthenticationFailure(self, status))

    def on_show(self) -> None:
        super().on_show()

        self.login_button.center_x = s.WINDOW_SIZE[0] / 2 - 60
        self.register_button.center_x = s.WINDOW_SIZE[0] / 2 + 60
