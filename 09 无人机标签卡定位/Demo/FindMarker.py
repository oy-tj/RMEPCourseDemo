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

import cv2
from robomaster import robot
import time

def sub_mission_pad_info_handler(mission_pad_info):
    MID, x, y, z = mission_pad_info
    print("Drone Mission Pad: MID {0}, x {1}, y {2}, z {3}".format(MID, x, y, z))
    img = tl_camera.read_cv2_image()
    cv2.imshow("Drone", img)
    cv2.waitKey(1)

if __name__ == '__main__':
    tl_drone = robot.Drone()
    tl_drone.initialize()
    #打开下视摄像头
    tl_camera = tl_drone.camera
    tl_camera.set_down_vision(setting=1)
    tl_camera.start_video_stream(display=False)
    # 订阅标签信息
    tl_drone._sub_drone_all_status(freq=10, callback=sub_mission_pad_info_handler)
    tl_flight = tl_drone.flight
    time.sleep(1)
    print('2')
    tl_flight.takeoff().wait_for_completed()
    tl_flight.forward(distance=100).wait_for_completed()
    tl_flight.backward(distance=100).wait_for_completed()
    print('2')
    tl_flight.land().wait_for_completed()
    print('3')
    # 取消订阅信息
    tl_drone._unsub_drone_all_status()
    cv2.destroyAllWindows()
    tl_camera.stop_video_stream()
    tl_drone.close()
