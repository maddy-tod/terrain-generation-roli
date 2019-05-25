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
import pygame
import pygame.midi

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RoliHandler :

    def __init__(self, controller):
        self.controller = controller
        pygame.init()
        pygame.midi.init()

        logger.info("Looking for devices")
        for i in range(4):
            logger.info(str(i) + " : " + str(pygame.midi.get_device_info(i)))

        input_id = 1
        logger.info("using input_id : %s" % input_id)
        self.midi_input = pygame.midi.Input(input_id)

        # sending midi to the output
        output_id = 3
        logger.info("using output_id : %s" % output_id)
        self.midi_output = pygame.midi.Output(output_id)

        # clear the display
        self.midi_output.write([[[0xc0, 0, 0], 0]])

        self.init_map()

    def run(self):

        if self.midi_input.poll():
            midi_events = self.midi_input.read(10)

            for event in midi_events:
                # event is [[status,data1,data2,data3],timestamp]
                data = event[0]

                if data[0] == 0xa0:

                    self.map[(data[1], data[2])] = 1

                    self.controller.update_terrain(self.map)

                # 0xcc means the button has been pressed - start again
                if data[0] == 0xcc:
                    self.reset()

                if data[0] == 0xaa:
                    print('RECIEVED ', (data[1], data[2]))

        self.controller.gui.after(100, self.run)

    def reset(self):
        self.init_map()
        self.controller.update_terrain(self.map)
        self.controller.update_label_text(text="Press the button to evolve!")

    def init_map(self):
        # create height map that is 0 everywhere
        self.map = {}
        for x in range(16):
            for y in range(16):
                self.map[x, y] = 0

    def send_val(self, x, y, val):
        adjusted_val = int(val * 128) + 128

        if x > 14 or y > 14 :
            return
        print('(x,y) : ', (x, y))

        try :
            if val > 0.5:
                self.midi_output.write([[[adjusted_val, x, y], 0]])
            else :
                self.midi_output.write([[[adjusted_val, x, y], 0]])
        except :

            print(x)
            print(y)
            print(val)
            print()

            self.midi_output.write([[[254, x, y], 0]])
