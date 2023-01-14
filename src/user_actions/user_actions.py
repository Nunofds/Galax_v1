from kivy import platform
from kivy.uix.relativelayout import RelativeLayout


# ----- Controls for keyboard key's for desktop -----
def _keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    self._keyboard.unbind(on_key_up=self._on_keyboard_up)
    self._keyboard = None


def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'left':
        self.current_speed_x = self.SPEED_X
    elif keycode[1] == 'right':
        self.current_speed_x = -self.SPEED_X
    return True


def _on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0
    return True


# check if user is in the desktop or not
def is_desktop(self):
    """ Check if user is on desktop or not

    :return: True or False
    :rtype: Boolean
    """
    if platform in ('linux', 'win', 'macosx'):
        return True
    return False


# ----- end controls for keyboard key's for desktop -----

# ----- controls on keybord for mobile -----
def on_touch_down(self, touch):
    if not self.state_game_over and self.state_game_has_started:
        if touch.x < self.width / 2:
            self.current_speed_x = self.SPEED_X
        else:
            self.current_speed_x = -self.SPEED_X
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    self.current_speed_x = 0

# ----- end controls on keybord for mobile -----
