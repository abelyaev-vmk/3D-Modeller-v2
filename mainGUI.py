import numpy as np
from GUI_consts import *
from CommonFunctions import get_image_size, MyDict, stderr
from ImageProperties import ImageObject, ImageProperties
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivy.core.window import Window, WindowBase
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from os import getcwd
from os.path import isfile
import warnings


ImageObjects = ImageProperties(G_image_path)


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
        self.widgets = MyDict()
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
        self.current_touches = []

        self.prev_draw_point = None
        self.colors = MyDict.from_dictionary({'Ground': (1, 0, 0),
                                              'Walls': (1, 1, 0),
                                              'Sky': (0, 0, 1),
                                              'Motion': (0, 1, 0)})
        print 'colors:', self.colors

    def add_point(self, point):
        if self.in_process_action_type is None:
            return
        self.current_points.append(point)

    def add_touch(self, touch):
        if self.in_process_action_type is None:
            return
        self.current_touches.append(touch)

    def add_object(self):
        if self.in_process_action_type is not None and self.current_points and self.current_points.__len__() > 2:
            ImageObjects.add(ImageObject(points=self.current_points,
                                         kivy_touches=self.current_touches,
                                         type=self.in_process_action_type))
            print 'Object added: %s %s' % (self.in_process_action_type, self.current_points.__str__())
        self.in_process_action_type = None
        self.current_points = []
        self.prev_draw_point = None

    def draw_point(self, touch):
        if not self.in_process_action_type:
            self.prev_draw_point = None
            return
        if self.prev_draw_point:
            image_widget.draw_line(self.prev_draw_point, touch, self.colors[self.in_process_action_type])
        self.prev_draw_point = touch

    def on_open_button_pressed(self):
        image_widget.source = self.widgets['TextInput'].text
        image_widget.size = get_image_size(image_widget.source)
        ImageObjects.copy(ImageProperties(image_widget.source))
        self.on_clear_button_pressed()

    def on_calculate_button_pressed(self):
        self.add_object()
        pass

    def on_load_button_pressed(self):
        self.add_object()
        ImageObjects.copy(ImageProperties.load(path=image_widget.source[:-4] + '_POINTS_DATA.3dm'))
        image_widget.draw_all_lines()

    def on_save_button_pressed(self):
        self.add_object()
        ImageObjects.save(path=image_widget.source[:-4] + '_POINTS_DATA.3dm')

    def on_clear_button_pressed(self):
        global ImageObjects, image_widget
        self.in_process_action_type = None
        image_widget.clear()

    def on_motion_button_pressed(self):
        self.add_object()
        self.in_process_action_type = 'Motion'

    def on_ground_button_pressed(self):
        self.add_object()
        self.in_process_action_type = 'Ground'

    def on_walls_button_pressed(self):
        self.add_object()
        self.in_process_action_type = 'Walls'

    def on_sky_button_pressed(self):
        self.add_object()
        self.in_process_action_type = 'Sky'

    def on_render_button_pressed(self):
        self.add_object()
        print >>stderr, 'RENDER:'
        print ImageObjects.__str__()
        print ImageObjects.objects


buttons_widget = ButtonsWidget()


class ImageWidget(Image):
    def __init__(self, source=G_image_path):
        super(ImageWidget, self).__init__()
        self.source = source
        self.size = get_image_size(G_image_path)
        self.widget_prop = 1, 1

    def on_touch_down(self, touch):
        if not self.collide_point(touch.x, touch.y):
            return
        print self.collide_point(touch.x, touch.y)
        buttons_widget.add_touch(touch)
        buttons_widget.draw_point(touch)
        buttons_widget.add_point(self.get_image_point((touch.x, touch.y)))

    def clear(self):
        for obj in self.canvas.children:
            if type(obj) == Line:
                self.canvas.remove(obj)

    def draw_line(self, touch1, touch2, (r, g, b)):
        print >>stderr, 'DRAW!'
        with self.canvas:
            Color(r, g, b)
            Line(points=touch1.pos + touch2.pos, width=5)

    def draw_all_lines(self):
        for key, itself in ImageObjects:
            if itself is None or itself is []:
                continue
            r, g, b = buttons_widget.colors[key]
            print "KEYKEYKEYKEY", key, "COLOR", (r, g, b)
            with self.canvas:
                Color(r, g, b)
                line = Line(width=5)
                for touches in ImageObjects.kivy_objects[key]:
                    print "TOUCHES!!!", touches
                    for touch in touches:
                        print "ONE TOUCH", touch
                        line.points += touch.x, touch.y
                print line.points

    def get_image_point(self, (x, y)):
        win_size = self.size
        img_size = map(float, get_image_size(self.source))
        win_prop, img_prop = win_size[0] / win_size[1], img_size[0] / img_size[1]
        if win_prop > 1 and img_prop > 1:
            t = float(win_size[1]) / img_size[1]
            ans_y = y / t
            ans_x = (x - (win_size[0] - img_size[0] * t) * .5) / t
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
