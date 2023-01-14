from kivy import Config, platform
from kivy.core.audio import SoundLoader

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '500')

from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
import random
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty

# Kivy Builder
Builder.load_file("menu.kv")


# ----- Main Interface kv -----
class MainWidget(RelativeLayout):
    # ----- imports -----
    from src.transforms.transforms import transform, transform_2d, transform_perspetive
    from src.user_actions.user_actions import _on_keyboard_up, _on_keyboard_down, _keyboard_closed, on_touch_down, \
        on_touch_up, is_desktop
    # ----- end imports -----

    # ----- VARIABLES -----
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    # Vertical lines
    V_NB_LINES = 10  # number of lines
    V_LINES_SPACING = .2  # percentage in screen width
    vertical_lines = []

    # Horizontal lines
    H_NB_LINES = 10  # number of lines
    H_LINES_SPACING = .2  # percentage in screen width
    horizontal_lines = []

    # deplacement auto y
    SPEED = 0.8
    current_offset_y = 0
    current_y_lop = 0

    # deplacement x
    SPEED_X = 2.0
    current_offset_x = 0
    current_speed_x = 0

    # construct tiles
    NB_TILES = 4
    tiles = []
    tiles_coordinates = []

    # Ship (vaisseau)
    ship = None
    SHIP_WIDTH = .08
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    # Game Over
    state_game_over = False
    # state to know if the game has started
    state_game_has_started = False

    # titles
    menu_title = StringProperty("G A L A X")
    menu_button_title = StringProperty("S T A R T")

    # score
    score_txt = StringProperty()

    # SOUNDS
    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    # ----- END VARIABLES -----

    # constructor
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # sounds init
        self.init_audio()
        # Create lines
        self.init_vertical_lines()
        self.init_horizontal_lines()
        # Create tiles
        self.init_tiles()
        # Create ship
        self.init_ship()
        # Generate tiles
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        # reset game
        self.reset_game()

        # Controls for keyboard key's
        if self.is_desktop():  # if we have a config to desktop we control with de keybord, else with screen touch
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        # schedule_interval to refresh 'graphics'
        Clock.schedule_interval(self.update, 1.0 / 60.0)

        # sounds
        self.sound_galaxy.play()

    # ----- RESTART GAME -----
    def reset_game(self):
        self.current_offset_x = 0
        self.current_y_lop = 0
        self.current_speed_x = 0
        self.current_offset_y = 0
        self.tiles_coordinates = []
        self.score_txt = 'SCORE: ' + str(self.current_y_lop)
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.state_game_over = False

    def init_audio(self):
        self.sound_begin = SoundLoader.load('src/audio/begin.wav')
        self.sound_galaxy = SoundLoader.load('src/audio/galaxy.wav')
        self.sound_gameover_impact = SoundLoader.load('src/audio/gameover_impact.wav')
        self.sound_gameover_voice = SoundLoader.load('src/audio/gameover_voice.wav')
        self.sound_music1 = SoundLoader.load('src/audio/music1.wav')
        self.sound_restart = SoundLoader.load('src/audio/restart.wav')

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_gameover_impact.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_galaxy.volume = .60

    # ----- SHIP -----
    def init_ship(self):
        """ Initiation canvas construction of the ship

        :return:
        :rtype:
        """
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship_coordinates(self):
        """ Update the coordinates of the ship in canvas

        :return:
        :rtype: any
        """
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        half_width = (self.SHIP_WIDTH * self.width) / 2
        ship_height = self.SHIP_HEIGHT * self.height

        self.ship_coordinates[0] = (center_x - half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + half_width, base_y)

        # TRANSFORM IN PERSPECTIVE VIEW
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    # ----- SHIP COLLISSIONS -----
    def check_ship_collisions(self):
        """ Check ship collisions

        :return: Return True of False
        :rtype: Boolean
        """
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_lop + 1:
                return False
            if self.chec_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def chec_ship_collision_with_tile(self, ti_x, ti_y):
        """ Check if ship have a collision with the tile

        :param ti_x: tile coordinates on x
        :type ti_x: int
        :param ti_y: tile coordinates on y
        :type ti_y: int
        :return: True or False
        :rtype: Boolean
        """
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    # END SHIP COLLISSIONS
    # ----- END SHIP -----

    # ----- VERTICAL LINES -----
    def init_vertical_lines(self):
        """ Generate the canvas for vertical lines

        :return:
        :rtype:
        """
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def update_vertical_lines(self):
        """ Update vertical lines in canvas

        :return:
        :rtype:
        """
        start_index = -int(self.V_NB_LINES / 2) + 1
        for i in range(start_index, start_index + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, int(self.height))
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    # ----- HORIZONTAL LINES -----
    def init_horizontal_lines(self):
        """ Generate the canvas for horizontal lines

        :return: The lines in canvas
        :rtype:
        """
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        """ Update horizontal lines in canvas

        :return:
        :rtype:
        """
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)

        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    # ----- END VERTICAL AND HORIZONTAL LINES -----

    # ----- LINES INDEX -----
    def get_line_x_from_index(self, index):
        """ Get the index of the line in x axis

        :param index: the index of the line in x axis
        :type index: int
        :return: Return the value of x index
        :rtype: int
        """
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        """ Get the index of the line in y axis

        :param index: the index of the line in y axis
        :type index: int
        :return: Return the value of y index
        :rtype: int
        """
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    # ----- END LINES INDEX -----

    # ----- TILES -----
    def init_tiles(self):
        """ Generate the canvas and the tiles (Quad)

        :return:
        :rtype:
        """
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        """ Generate x tiles inline for start the game (x=0 , y=number of incrementation)

        :return: Return a list with the x and y coords
        :rtype: list
        """
        for i in range(0, 5):
            self.tiles_coordinates.append((0, i))

    def get_tile_coordinates(self, ti_x, ti_y):
        """ Get the x and y coordinates of the tile

        :param ti_x: x tile coords
        :type ti_x: int
        :param ti_y: y tile coords
        :type ti_y: int
        :return: Return x and y values as a tuple
        :rtype: tuple
        """
        ti_y = ti_y - self.current_y_lop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def generate_tiles_coordinates(self):
        """ Generate the coordinates of the tiles and prevent the ship to going out

        :return:
        :rtype:
        """
        last_y = 0
        last_x = 0

        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_lop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        for _ in range(len(self.tiles_coordinates), self.NB_TILES):
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            r = random.randint(0, 2)

            # verification to don't depassing borders limit
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = -1

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            elif r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            last_y += 1

    def update_tiles(self):
        """ Update the position of the tiles in canvas

        :return:
        :rtype:
        """
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]

            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0] + 1, tile_coordinates[1] + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    # ----- END TILES -----

    # ----- UPDATE -----
    def update(self, dt) -> any:
        """ Loop to update game and make the game works.
        The fonction loop permits update the differents canvas.

        :param dt: datatime
        :type dt: float
        :return:
        :rtype: any
        """
        time_factor = dt * 60

        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship_coordinates()

        # advance in the game if not Game Over and if we click in start button
        if not self.state_game_over and self.state_game_has_started:
            # move to front (y)
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_lop += 1
                self.score_txt = 'SCORE: ' + str(self.current_y_lop)
                self.generate_tiles_coordinates()

            # move to left/right (x)
            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        # chec if ship is in the tile (GAME OVER)
        if not self.check_ship_collisions() and not self.state_game_over:
            self.state_game_over = True
            # sounds
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_voice_game_over, 1.5)
            self.sound_music1.stop()
            # end sounds
            self.menu_title = 'GAME OVER'
            self.menu_button_title = 'RESTART'
            self.menu_widget.opacity = 1
            print('GAME OVER')

    # ----- ENDS UPDATE -----

    # Play voice game over with a delay
    def play_voice_game_over(self, dt):
        self.sound_gameover_voice.play()

    # End play voice game over with a delay

    # ----- Click button to start the game -----
    def on_menu_button_pressed(self):
        # sounds
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music1.play()

        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        print("BOUTON")

    # ----- end Click button to start the game -----


# ***** Main Application *****
class MainApp(App):
    pass


if __name__ == '__main__':
    MainApp().run()