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
import logging
from GUI import TerrainGenApp
from RoliHandler import RoliHandler
from TerrainGen import quantum_tartan
import numpy as np

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class MainHandler:
    def __init__(self):
        print("Made a handler")
        self.gui = None
        self.user_input = None

        self.current_theta = 0.1

    def update_terrain(self, map_):
        self.gui.draw_terrain(map_)

    def update_label_text(self, text=None):
        if not text:
            text = 'theta = ' + str(self.current_theta)
        self.gui.label_canvas.itemconfigure(self.gui.label_text, text=text)

    def button_pressed(self):

        new_map, grid = quantum_tartan(self.user_input.map, self.current_theta)

        self.gui.draw_terrain(new_map, terrain=None)

        self.update_label_text()

        self.current_theta += 0.1

        if self.current_theta > np.pi:
            self.current_theta = 0

        # send to Roli
        i = 0
        for point, val in new_map.items():
            x, y = point
            self.user_input.send_val(x, y, val)
            i +=1

        print("sent ", i, " items")


if __name__ == "__main__":

    m = MainHandler()
    app = TerrainGenApp(m)
    m.gui = app

    user_input = RoliHandler(m)
    user_input.reset()

    m.user_input = user_input

    user_input.run()

    while app.running:
        app.mainloop()
