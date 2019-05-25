# -*- coding: utf-8 -*-

# Copyright 2019 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font as tkfont


class TerrainGenApp(tk.Tk):

    def __init__(self, controller, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.controller = controller

        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.running = True
        self.geometry("1000x700")

        tk.Canvas(self, width=375, height=70).grid(row=0, column=0)

        button_container = tk.Frame(self)
        button_container.grid(row=0, column=1, pady=10)
        self.basic_button = tk.Button(button_container, text="Make a new terrain!",
                                 command=lambda: self.evolve_state(),
                                 height=2, width=20)
        self.basic_button.grid(row=0, column=0)

        self.terrain_canvas = tk.Canvas(self, width=370, height=370, bg='red')

        self.terrain_img_canvas = None
        self.terrain_img_imgtk = None
        self.draw_terrain(map_=self._base_terrain())

        self.terrain_canvas.grid(row=1, column=1)

        label_font = tkfont.Font(family='Helvetica', size=18)
        self.label_canvas = tk.Canvas(self, width=370, height=100)
        self.label_canvas.grid(row=2, column=1)

        self.label_text = self.label_canvas.create_text((190, 50), text="Press the button to evolve!", font=label_font)

    def _on_closing(self):
        self.running = False
        self.destroy()

    def draw_terrain(self, map_, terrain=[5 / 16, 6 / 16, 9 / 16, 12 / 16, 14 / 16]):

        self.plot_height(Z=map_, zoom=25, terrain=terrain)

        img = Image.open('temp.png')
        self.terrain_img_imgtk = ImageTk.PhotoImage(img)

        if not self.terrain_img_canvas:
            self.terrain_img_canvas = self.terrain_canvas.create_image((0, 0), image=self.terrain_img_imgtk,
                                                                       anchor=tk.NW, tag='terrain')
        else :
            self.terrain_canvas.itemconfig('terrain', image=self.terrain_img_imgtk)

    def plot_height(self, Z, terrain=[5 / 16, 6 / 16, 9 / 16, 12 / 16, 14 / 16], zoom=None):
        # display a heightmap as the above image
        # displayed image is a terrain map by default
        img = self.height2image(Z, terrain=terrain)
        if zoom:
            img = img.resize((zoom * img.size[0], zoom * img.size[0]), Image.ANTIALIAS)
        img.save('temp.png')

    def height2image(self, Z, terrain=None):
        # converts a heightmap z into a PIL image
        # for terrain=None, this is a black and white image with white for Z[x,y]=1 and black for Z[x,y]=0
        # otherwise, the values in terrain are used as thresholds between sea and beach, beach and grass, etc
        image = {}

        for pos in Z:

            if terrain:
                if Z[pos] < terrain[0]:
                    image[pos] = (50, 120, 200)
                elif Z[pos] < terrain[1]:
                    image[pos] = (220, 220, 10)
                elif Z[pos] < terrain[2]:
                    image[pos] = (100, 200, 0)
                elif Z[pos] < terrain[3]:
                    image[pos] = (75, 150, 0)
                elif Z[pos] < terrain[4]:
                    image[pos] = (200, 200, 200)
                else:
                    image[pos] = (255, 255, 255)
            else:
                z = int(255 * Z[pos])
                image[pos] = (z, z, z)

        img = Image.new('RGB', max(Z.keys()))
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                img.load()[x, y] = image[x, y]
        return img

    def _base_terrain(self):
        # create height map that is 0 everywhere
        Z = {}
        for x in range(16):
            for y in range(16):
                Z[x, y] = 0
        return Z

    def evolve_state(self):
        self.controller.button_pressed()
