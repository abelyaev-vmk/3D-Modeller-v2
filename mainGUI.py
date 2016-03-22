import numpy as np
from MainConsts import *
from CommonFunctions import get_image_size, MyDict, stderr
from ImageProperties import ImageObject, ImageProperties
from CameraProperties import CameraProperties
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle
from kivy.core.window import Window, WindowBase
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget, Canvas
from os import getcwd, chdir
from os.path import exists
import warnings

ImageObjects = ImageProperties(G_image_path)
Project = G_start_project
chdir(Project)


class ButtonsWidget(GridLayout):
    def __init__(self):
        super(ButtonsWidget, self).__init__()
        self.rows = 2
        self.path_input = TextInput(text=G_start_project)
        self.open_button = Button(text='Open')
        self.load_data_button = Button(text='Load')
        self.save_data_button = Button(text='Save')
        self.clear_data_button = Button(text='Clear')
        self.quit_button = Button(text='Quit')
        self.ground_button = Button(text='Ground(0)')
        self.walls_button = Button(text='Walls(0)')
        self.sky_button = Button(text='Sky(0)')
        self.motion_path_button = Button(text='Motion(0)')
        self.calculate_scene_button = Button(text='Calculate Scene')
        self.render_scene_button = Button(text='Render Scene')
        self.widgets = MyDict(length=3)
        self.buttons = (self.path_input, self.load_data_button, self.ground_button,
                        self.sky_button, self.motion_path_button, self.quit_button, self.open_button,
                        self.save_data_button, self.walls_button,
                        self.clear_data_button, self.calculate_scene_button, self.render_scene_button)
        self.reactions = (self.on_load_button_pressed, self.on_ground_button_pressed, self.on_sky_button_pressed,
                          self.on_motion_button_pressed, exit, self.on_open_button_pressed, self.on_save_button_pressed,
                          self.on_walls_button_pressed, self.on_clear_button_pressed, self.on_calculate_button_pressed,
                          self.on_render_button_pressed)
        self.on_buttons_count = MyDict.from_dictionary({
            'Ground': 0,
            'Walls': 0,
            'Sky': 0,
            'Motion': 0,
        }, length=6)
        for i, w in enumerate(self.buttons):
            self.add_widget(w)
            self.widgets['TextInput' if i == 0 else w.text] = w
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

        self.cp = None

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

            self.add_button_count(self.in_process_action_type)
            self.upgrade_buttons_count()
        self.in_process_action_type = None
        self.current_points = []
        self.current_touches = []
        self.prev_draw_point = None

    def draw_point(self, touch):
        if not self.in_process_action_type:
            self.prev_draw_point = None
            return
        if self.prev_draw_point:
            image_widget.draw_line_from_touches(self.prev_draw_point, touch, self.colors[self.in_process_action_type])
        self.prev_draw_point = touch

    def upgrade_buttons_count(self):
        for key in self.on_buttons_count:
            self.widgets[key].text = '%s(%d)' % (key, self.on_buttons_count[key])

    def add_button_count(self, key):
        self.on_buttons_count[key] += 1

    def on_open_button_pressed(self):
        try:
            chdir('../%s' % self.widgets['TextInput'].text)
            global Project
            Project = self.widgets['TextInput'].text
            image_widget.source = '../%s/%s' % (Project, G_image_path)
            image_widget.size = get_image_size(G_image_path)
            ImageObjects.copy(ImageProperties(G_image_path))
            print image_widget.size
            self.on_clear_button_pressed()
        except WindowsError:
            pass

    def on_load_button_pressed(self):
        global ImageObjects
        self.add_object()
        ImageObjects = ImageProperties.load()
        image_widget.draw_all_lines()

    def on_save_button_pressed(self):
        self.add_object()
        ImageObjects.save()

    def on_clear_button_pressed(self):
        global ImageObjects, image_widget
        self.in_process_action_type = None
        for key in self.on_buttons_count:
            self.on_buttons_count[key] = 0
            self.widgets[key].text = '%s(0)' % key
        image_widget.clear()

    def on_motion_button_pressed(self):
        if self.in_process_action_type:
            self.add_object()
        else:
            self.in_process_action_type = 'Motion'

    def on_ground_button_pressed(self):
        if self.in_process_action_type:
            self.add_object()
        else:
            self.in_process_action_type = 'Ground'

    def on_walls_button_pressed(self):
        if self.in_process_action_type:
            self.add_object()
        else:
            self.in_process_action_type = 'Walls'

    def on_sky_button_pressed(self):
        if self.in_process_action_type:
            self.add_object()
        else:
            self.in_process_action_type = 'Sky'

    def on_calculate_button_pressed(self):
        self.add_object()
        self.cp = CameraProperties(project=Project, image_path=G_image_path, ip=ImageObjects)
        self.cp.calculate()

    def on_render_button_pressed(self):
        self.add_object()
        if self.cp is not None and self.cp.calculated:
            self.cp.render()


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
        buttons_widget.add_touch(touch)
        buttons_widget.draw_point(touch)
        buttons_widget.add_point(self.get_image_point((touch.x, touch.y)))

    def clear(self):
        for obj in self.canvas.children:
            if type(obj) == Line:
                self.canvas.remove(obj)

    def draw_line_from_touches(self, touch1, touch2, (r, g, b)):
        print >> stderr, 'DRAW!'
        with self.canvas:
            Color(r, g, b)
            Line(points=touch1.pos + touch2.pos, width=2)

    def draw_lines_from_points(self, points, (r, g, b), width=2):
        with self.canvas:
            Color(r, g, b)
            Line(points=points, width=width)

    def draw_all_lines(self):
        for key, itself in ImageObjects:
            if itself is None or itself is []:
                continue
            lines = []
            for i, touches in enumerate(ImageObjects.kivy_objects[key]):
                buttons_widget.add_button_count(key)
                all_coordinates = map(lambda touch: [touch.x, touch.y], touches)
                lines.append([])
                for coordinate in all_coordinates:
                    lines[i] += coordinate
            for line in lines:
                self.draw_lines_from_points(line, buttons_widget.colors[key], width=2)
        buttons_widget.upgrade_buttons_count()

    def get_image_point(self, (x, y)):
        win_size = self.size
        img_size = map(float, get_image_size(self.source))
        ww, wh = win_size
        iw, ih = img_size
        win_prop, img_prop = ww / wh, iw / ih
        if win_prop > 1:
            if img_prop > 1:
                t = float(win_size[0]) / img_size[0]
                ans_x = x / t
                ans_y = (y - (win_size[1] - img_size[1] * t) * .5) / t

                print 'GET_IMAGE_POINT DEBUG'
                print win_prop, img_prop
                print t
                print '%s -> %s' % ((x, y).__str__(), (ans_x, ans_y).__str__())

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


if __name__ == '__main__':
    MainGUI().run()
