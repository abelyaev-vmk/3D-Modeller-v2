import numpy as np
from GUI_consts import *
from CommonFunctions import get_image_size
from ImageProperties import ImageObject, ImageProperties
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.window import Window, WindowBase
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from os import getcwd
from os.path import isfile
import warnings


ImageObjects = []


class ButtonsWidget(GridLayout):
    def __init__(self):
        super(ButtonsWidget, self).__init__()
        self.rows = 2
        self.path_input = TextInput(text=G_image_path)
        self.open_button = Button(text='Open')
        self.load_data_button = Button(text='Load')
        self.save_data_button = Button(text='Save')
        self.clear_data_button = Button(text='Clear')
        self.quit_button = Button(text='Quit')
        self.ground_button = Button(text='Ground(None)')
        self.walls_button = Button(text='Walls(0)')
        self.sky_button = Button(text='Sky(None)')
        self.motion_path_button = Button(text='Motion path(0)')
        self.calculate_scene_button = Button(text='Calculate Scene')
        self.render_scene_button = Button(text='Render Scene')
        self.widgets = {}
        self.buttons = (self.path_input, self.load_data_button, self.ground_button,
                        self.sky_button, self.motion_path_button, self.quit_button, self.open_button,
                        self.save_data_button, self.walls_button,
                        self.clear_data_button, self.calculate_scene_button, self.render_scene_button)
        self.reactions = (self.on_load_button_pressed, self.on_ground_button_pressed, self.on_sky_button_pressed,
                          self.on_motion_button_pressed, exit, self.on_open_button_pressed, self.on_save_button_pressed,
                          self.on_walls_button_pressed, self.on_clear_button_pressed, self.on_calculate_button_pressed,
                          self.on_render_button_pressed)

        for i, w in enumerate(self.buttons):
            self.add_widget(w)
            self.widgets['TextInput' if i == 0 else w.text[:5]] = w
            if i > 0:
                w.on_press = self.reactions[i - 1]

        self.in_process_action_type = None
        self.current_points = []

    def add_touch(self, point):
        if self.in_process_action_type is None:
            return
        self.current_points.append(point)

    def add_object(self):
        if self.in_process_action_type is not None and self.current_points:
                ImageObjects.append(ImageObject(points=self.current_points, type=self.in_process_action_type))
        self.in_process_action_type = None
        self.current_points = []

    def on_open_button_pressed(self):
        image_widget.source = self.widgets['TextInput'].text
        image_widget.size = get_image_size(image_widget.source)

    def on_calculate_button_pressed(self):
        pass

    def on_motion_button_pressed(self):
        pass

    def on_load_button_pressed(self):
        pass

    def on_save_button_pressed(self):
        pass

    def on_clear_button_pressed(self):
        pass

    def on_ground_button_pressed(self):
        print 'lala'
        print ImageObjects[0].show() if ImageObjects else 'Empty'
        self.add_object()
        self.in_process_action_type = 'Ground'

    def on_walls_button_pressed(self):
        pass

    def on_sky_button_pressed(self):
        pass

    def on_render_button_pressed(self):
        pass


buttons_widget = ButtonsWidget()


class ImageWidget(Image):
    def __init__(self):
        super(ImageWidget, self).__init__()
        self.source = G_image_path
        self.size = get_image_size(G_image_path)
        self.widget_prop = 1, 1

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return
        print self.collide_point(touch.x, touch.y)
        buttons_widget.add_touch(self.get_image_point((touch.x, touch.y)))

    def get_image_point(self, (x, y)):
        win_size = self.size
        img_size = map(float, get_image_size(self.source))
        # print win_size, img_size, self.size
        win_prop, img_prop = win_size[0] / win_size[1], img_size[0] / img_size[1]
        # print win_prop, img_size
        if win_prop > 1 and img_prop > 1:
            t = float(win_size[1]) / img_size[1]
            ans_y = y / t
            ans_x = (x - (win_size[0] - img_size[0] * t) * .5) / t
            # print 'on Image: %f %f' % (ans_x, ans_y)
            return ans_x, ans_y
        return 0, 0


image_widget = ImageWidget()


class MainWidget(BoxLayout):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.orientation = 'vertical'
        self.add_widget(buttons_widget)
        self.add_widget(Widget())
        self.add_widget(image_widget)
        self.children[2].size_hint = 1, .18
        self.children[1].size_hint = 1, .03
        image_widget.widget_prop = 1, 1 - .21


main_widget = MainWidget()


class MainGUI(App):
    def build(self):
        return main_widget
        # return ButtonsWidget()
        # return ImageWidget()


if __name__ == '__main__':
    MainGUI().run()
