from sys import stderr, stdout


# Get size of image
def get_image_size(source):
    from PIL import Image
    return Image.open(source).size


class MyDict(dict):
    def __init__(self, length=5):
        super(MyDict, self).__init__()
        self.dict = {}
        self.length = length

    def __setitem__(self, key, value):
        self.dict[key[:self.length]] = value

    def __getitem__(self, key):
        try:
            return self.dict[key[:self.length]]
        except KeyError:
            print >> stderr, 'Bad key %s' % key.__str__()
            return None

    @staticmethod
    def from_dictionary(dictionary, length=3):
        new_dictionary = MyDict(length=length)
        for key in dictionary:
            print key, dictionary[key]
            new_dictionary[key] = dictionary[key]
            print key, new_dictionary[key]
        print new_dictionary['Wall']
        return new_dictionary

#     import Tkinter
#
#
# import tkFileDialog
# import numpy as np
# from moviepy.editor import *
# from scipy.misc import imsave
# import os
# from kivy.uix.textinput import TextInput
# from random import random
# from kivy.app import App
# from kivy.uix.widget import Widget
# from kivy.uix.button import Button
# from kivy.graphics import Color, Ellipse, Line, Rectangle
# from kivy.core.window import Window
# from shutil import rmtree
# from tempfile import tempdir, mkdtemp
# from os import remove, makedirs
# from os.path import isdir, exists, isfile
# import collections
#
# pad = 200;
# speed = 25;
#
#
# class iButton(Button):
#     pass
#
#
# class Video:
#     def __init__(filename, self):
#         self.video = VideoFileClip(filename)
#         self.next = 0
#
#     def GetNextFrame(self):
#         directory = "frames1"
#         imsave(directory + "/test" + str(self.next) + ".png", self.video.get_frame(self.next / int(self.video.fps)))
#         file_name1111 = directory + "/test" + str(self.next) + ".png"
#         self.next += 50;
#         return file_name1111
#
#
# class MyPaintWidget(Widget):
#     def __init__(self):
#         super(MyPaintWidget, self).__init__()
#         self._keyborad = Window.request_keyboard(self._keyboard_closed, self)
#         self._keyborad.bind(on_key_down=self._on_keyboard_down)
#         Window.size = (1366, 768)
#         self.size = Window.size
#         # if smoke true - user can draw rectangle
#         self.smoke = False
#         # if fire true - user can draw rectangle
#         self.fire = False
#         # list with points of fire rectangle
#         self.rectanglePoints = []
#         # number of current frame
#         self.numberOfFrame = 0;
#         # if video open isVideoOpen = True
#         self.isVideoOpen = False
#         # video
#         self.video = None
#         # filename of result txt file
#         self.txtFilename = ""
#         # path to temp directory
#         self.dirPath = ""
#         # dictionary with points
#         self.dictionary = {}
#         self.Forest = ""
#         self.In = ""
#         self.Out = ""
#         self.start = 0
#         self.finish = 0
#         self.type = "None"
#         self.move = False
#
#     def _keyboard_closed(self):
#         print('My keyboard have been closed!')
#         self._keyboard.unbind(on_key_down=self._on_keyboard_down)
#         self._keyboard = None
#
#     def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
#
#         # Keycode is composed of an integer + a string
#         # If we hit escape, release the keyboard
#         if keycode[1] == 'f':
#             self.NextFrame()
#         if keycode[1] == 'a':
#             self.DrawSmoke()
#         if keycode[1] == 'd':
#             self.DrawFire()
#         if keycode[1] == 'z':
#             self.PrevFrame()
#         # Return True to accept the key. Otherwise, it will be used by
#         # the system.
#         return True
#
#     def PrevFrame(self):
#         self.numberOfFrame -= 2 * speed
#         self.NextFrame()
#
#     def NextFrame(self):
#         for line in self.canvas.children:
#             if (type(line) == Line):
#                 self.canvas.children.remove(line)
#         for obj in self.canvas.children:
#             if type(obj) == Rectangle:
#                 self.rect = obj
#         filename = self.GetFrameFilename()
#         if (filename == None):
#             self.rect.size = (0, 0)
#         else:
#             self.rect.source = filename
#
#     def openVideoFile(self):
#         # open file explorer
#         root = Tkinter.Tk()
#         root.withdraw()
#         # get video filename
#         filename = tkFileDialog.askopenfilename(parent=root, title='Open file to encrypt')
#
#         try:
#             self.video = VideoFileClip(filename)
#             print self.video.fps
#         except Exception:
#             print "Error in opening file - " + filename
#             return None
#         # create default txt filename
#         self.txtFilename = filename[:filename.rfind(".")] + "_label.txt"
#         # display txt filename
#         self.ids.PathSaveFile.text = self.txtFilename
#         # create temp directory for frames from video
#         # self.dirPath = mkdtemp()
#         self.dirPath = "asdf"
#         makedirs("asdf")
#         print self.video.duration
#         # set number of frame
#         self.numberOfFrame = 0
#         # change winow size
#         Window.size = (self.video.size[0], self.video.size[1] + pad)
#         self.size = (self.video.size[0], self.video.size[1] + pad)
#
#         self.firstFrame = True
#         # find rectangle
#         for obj in self.canvas.children:
#             if type(obj) == Rectangle:
#                 self.rect = obj
#         # set rectangle size
#         self.rect.size = (self.size[0], self.size[1] - pad)
#         # set frame to rectangle
#         self.rect.source = self.GetFrameFilename()
#
#     # return filename of frame from video
#     def GetFrameFilename(self):
#         # check if video open
#         if (self.video == None):
#             print "Error! Video doesn't open!"
#             return None
#         if (self.firstFrame):
#             imsave(self.dirPath + "/temp0.png", self.video.get_frame(self.numberOfFrame / self.video.fps))
#             self.firstFrame = False
#             self.dictionary[self.numberOfFrame] = {}
#             self.dictionary[self.numberOfFrame]["smoke"] = []
#             self.dictionary[self.numberOfFrame]["fire"] = []
#             return self.dirPath + "/temp0.png"
#         else:
#             # increase number of frame
#             self.numberOfFrame = int(self.numberOfFrame) + speed
#             if (self.numberOfFrame >= self.video.duration * self.video.fps):
#                 self.numberOfFrame = int(self.numberOfFrame) - speed
#                 self.Video = None
#                 return None
#             self.dictionary[self.numberOfFrame] = {}
#             self.dictionary[self.numberOfFrame]["smoke"] = []
#             self.dictionary[self.numberOfFrame]["fire"] = []
#             # save frame from video
#             imsave(self.dirPath + "/temp" + str(self.numberOfFrame) + ".png",
#                    self.video.get_frame(int(self.numberOfFrame / self.video.fps)))
#             print self.numberOfFrame / (self.video.fps * self.video.duration) * 100
#             return self.dirPath + "/temp" + str(self.numberOfFrame) + ".png"
#
#     def DrawSmoke(self):
#         # check if video open
#         if (self.video == None):
#             print "Error! Video doesn't open!"
#             return None
#         self.smoke = True
#         self.fire = False
#
#     def DrawFire(self):
#         # check if video open
#         if (self.video == None):
#             print "Error! Video doesn't open!"
#             return None
#         self.fire = True
#         self.smoke = False
#
#     def CleanSmoke(self):
#         points = self.dictionary.get(self.numberOfFrame)
#         if (points == None):
#             return None
#
#         pointsList = points.get("smoke")
#         if (points == None):
#             return None
#         else:
#             for points in pointsList:
#                 # print "asdf"
#                 for line in self.canvas.children:
#                     if type(line) == Line:
#                         for i in range(0, 4):
#                             if line.points.count(points[i]) != 2:
#                                 break
#                         else:
#                             self.canvas.children.remove(line)
#             self.dictionary.get(self.numberOfFrame)["smoke"] = []
#
#     def CleanFire(self):
#         points = self.dictionary.get(self.numberOfFrame)
#         if (points == None):
#             return None
#
#         pointsList = points.get("fire")
#         # print "fire"
#         # print points
#         if (points == None):
#             return None
#         else:
#             for points in pointsList:
#                 for line in self.canvas.children:
#                     if type(line) == Line:
#                         for i in range(0, 4):
#                             if line.points.count(points[i]) != 2:
#                                 break
#                         else:
#                             self.canvas.children.remove(line)
#             self.dictionary.get(self.numberOfFrame)["fire"] = []
#
#     def FinishFire(self):
#         # check if video open
#         if (self.video == None):
#             print "Error! Video doesn't open!"
#             return None
#         self.finish = self.numberOfFrame
#
#     def StartFire(self):
#         # check if video open
#         if (self.video == None):
#             print "Error! Video doesn't open!"
#             return None
#         self.start = self.numberOfFrame
#
#     def In23(self):
#         # check if video open
#         if (self.video == None):
#             print "Error! Video doesn't open!"
#             return None
#         print "asdf"
#         self.type = "In"
#         self.ids.LInfo.text = self.type
#
#     def Out23(self):
#         # check if video open
#         if (self.video == None):
#             print "Error! Video doesn't open!"
#             return None
#         self.type = "Out"
#         self.ids.LInfo.text = self.type
#
#     def Forest23(self):
#         # check if video open
#         if (self.video == None):
#             print "Error! Video doesn't open!"
#             return None
#         self.type = "Forest"
#         self.ids.LInfo.text = self.type
#
#     def Quit(self):
#         print self.dirPath
#         if (isdir(self.dirPath)):
#             rmtree(self.dirPath)
#         App.get_running_app().stop()
#
#     def on_touch_down(self, touch):
#         super(MyPaintWidget, self).on_touch_down(touch)
#         color = (random(), 1, 1)
#         if (0 <= touch.y < self.size[1] - pad and 0 <= touch.x < self.size[0] and (self.smoke or self.fire)):
#             self.move = True
#             self.rectanglePoints.append(touch.x)
#             self.rectanglePoints.append(touch.y)
#             x = touch.x
#             y = touch.y
#             with self.canvas:
#                 if (self.smoke):
#                     Color(1, 0, 0)
#                 else:
#                     Color(0, 0, 1)
#                 touch.ud['line'] = Line(rectangle=(x, y, 0, 0))
#
#     def on_touch_move(self, touch):
#         if 0 <= touch.y < self.size[1] - pad and 0 <= touch.x < self.size[0] and (
#             self.smoke or self.fire) and self.move:
#             x = self.rectanglePoints[0]
#             y = self.rectanglePoints[1]
#             touch.ud['line'].rectangle = (x, y, touch.x - x, touch.y - y)
#
#     def on_touch_up(self, touch):
#         if (0 <= touch.y < self.size[1] - pad and 0 <= touch.x < self.size[0] and (self.smoke or self.fire)):
#             self.move = False
#             self.rectanglePoints.append(touch.x)
#             self.rectanglePoints.append(touch.y)
#             if (self.smoke):
#                 # self.dictionary[self.numberOfFrame]["smoke"] = self.rectanglePoints
#                 self.dictionary[self.numberOfFrame]["smoke"].append(self.rectanglePoints)
#
#                 # print "smoke dict"
#                 # print self.dictionary[self.numberOfFrame]["smoke"]
#             else:
#                 self.dictionary[self.numberOfFrame]["fire"].append(self.rectanglePoints)
#                 # print "fire dict"
#                 # print self.dictionary[self.numberOfFrame]["fire"]
#             self.smoke = False
#             self.fire = False
#             self.rectanglePoints = []
#
#     def SaveResult(self):
#         filename = self.ids.PathSaveFile.text
#         if (not (".txt" in filename)):
#             print "Error in text filename"
#         if isfile(filename):
#             i = 0
#             while (1):
#                 filename = filename.replace(".txt", str(i) + ".txt")
#                 if isfile(filename):
#                     i += 1
#                     continue
#                 else:
#                     break
#         f = open(filename, 'w')
#         f.write("type " + self.type + "\n")
#         f.write("start %s\n" % self.start)
#         f.write("finish %s\n" % self.finish)
#         self.dictionary = collections.OrderedDict(sorted(self.dictionary.items()))
#         for k, v in self.dictionary.iteritems():
#             f.write(str(k))
#             f.write(" smoke ")
#             if v.get("smoke") != None:
#                 for item in v["smoke"]:
#                     f.write("%s " % item)
#             else:
#                 f.write(" 0 0 0 0 ")
#             f.write(" fire ")
#             if v.get("fire") != None:
#                 for item in v["fire"]:
#                     f.write("%s " % item)
#             else:
#                 f.write("0 0 0 0")
#             f.write("\n")
#         f.close()
#
#
# class MyPaintApp(App):
#     def build(self):
#         return MyPaintWidget()
#
#
# if __name__ == '__main__':
#     MyPaintApp().run()
