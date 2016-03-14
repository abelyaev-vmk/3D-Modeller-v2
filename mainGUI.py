import numpy as np
from GUI_consts import *
from CommonFunctions import get_image_size
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
        self.render_scene_button = Button(text='Render Scene')
        self.widgets = {}
        self.buttons = (self.path_input, self.load_data_button, self.ground_button,
                        self.sky_button, self.quit_button, self.open_button,
                        self.save_data_button, self.walls_button,
                        self.clear_data_button, self.render_scene_button)
        self.reactions = (self.on_load_button_pressed, self.on_ground_button_pressed, self.on_sky_button_pressed,
                          exit, self.on_open_button_pressed, self.on_save_button_pressed, self.on_walls_button_pressed,
                          self.on_clear_button_pressed, self.on_render_button_pressed)

        for i, w in enumerate(self.buttons):
            self.add_widget(w)
            self.widgets['TextInput' if i == 0 else w.text] = w
            if i > 0:
                w.on_press = self.reactions[i - 1]

    def on_open_button_pressed(self):
        image_widget.source = self.widgets['TextInput'].text
        image_widget.size = get_image_size(image_widget.source)

    def on_load_button_pressed(self):
        pass

    def on_save_button_pressed(self):
        pass

    def on_clear_button_pressed(self):
        pass

    def on_ground_button_pressed(self):
        pass

    def on_walls_button_pressed(self):
        pass

    def on_sky_button_pressed(self):
        pass

    def on_render_button_pressed(self):
        pass


class ImageWidget(Image):
    def __init__(self):
        super(ImageWidget, self).__init__()
        self.source = G_image_path
        self.size = get_image_size(G_image_path)

    def on_touch_down(self, touch):
        print touch.x, touch.y


image_widget = ImageWidget()
buttons_widget = ButtonsWidget()


class MainWidget(BoxLayout):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.orientation = 'vertical'
        self.add_widget(buttons_widget)
        self.add_widget(image_widget)
        self.children[1].size_hint = 1, .2


main_widget = MainWidget()


class MainGUI(App):
    def build(self):
        return main_widget
        # return ButtonsWidget()
        # return ImageWidget()


if __name__ == '__main__':

    print Window.size
    MainGUI().run()
