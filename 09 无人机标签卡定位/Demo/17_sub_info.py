#无人机识别通行卡
# -*-coding:utf-8-*-
# Copyright (c) 2020 DJI.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import robomaster
from robomaster import robot
import time

def sub_mission_pad_info_handler(mission_pad_info):
    MID, x, y, z = mission_pad_info
    print("Drone Mission Pad: MID {0}, x {1}, y {2}, z {3}".format(MID, x, y, z))

if __name__ == '__main__':
    tl_drone = robot.Drone()
    time.sleep(1)
    tl_drone.initialize()
    print('1')
    # 订阅飞行器信息
    tl_drone._sub_drone_all_status(freq=10, callback=sub_mission_pad_info_handler)
    print('2')
    time.sleep(1)
    print('3')
    time.sleep(10)
    # 取消订阅信息
    tl_drone._unsub_drone_all_status()
    print('5')
    tl_drone.close()

