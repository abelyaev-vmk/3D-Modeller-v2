import numpy as np
from kivy.app import App
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from os import getcwd
from os.path import isfile
import warnings


from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from PIL import Image as PIL_Image


def define_size(path='image.jpg'):
    return PIL_Image.open(path).size


class ButtonsWidget(GridLayout):
    def __init__(self):
        self.cols = 1
        super(ButtonsWidget, self).__init__()
        self.add_widget(Label(text="1"))
        self.add_widget(Label(text="2"))
        self.add_widget(Label(text="3"))
        self.size = 20, 20


class ImageWidget(Widget):
    def __init__(self, image_path='image.jpg'):
        super(ImageWidget, self).__init__()
        self.rect = Image()
        self.rect.source = image_path
        self.size = define_size(image_path)
        self.rect.size = self.size
        self.add_widget(self.rect)


class MainGUI(GridLayout):
    def __init__(self):
        self.cols = 1
        size = define_size('image.jpg')
        self.size = size[0], size[1] * 1.3
        Window.size = map(int, self.size)
        super(MainGUI, self).__init__()
        self.add_widget(ButtonsWidget())
        self.add_widget(ImageWidget())
        self.children[1].size_hint = 1, 0.3


class GUIApp(App):
    def build(self):
        return ImageWidget()


if __name__ == '__main__':
    GUIApp().run()