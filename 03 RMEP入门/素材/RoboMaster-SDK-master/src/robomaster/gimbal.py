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


import struct
from . import module
from . import protocol
from . import action
from . import logger
from . import util
from . import dds


__all__ = ['Gimbal', 'GimbalMoveAction']


COORDINATE_NED = 0
COORDINATE_CUR = 1
COORDINATE_CAR = 2
COORDINATE_PNED = 3     # pitch NED mode
COORDINATE_YCPN = 4     # yaw CAR, pitch NED mode
COORDINATE_YCPO = 5     # yaw CAR, pitch OFFSET mode


class GimbalMoveAction(action.Action):
    _action_proto_cls = protocol.ProtoGimbalRotate
    _push_proto_cls = protocol.ProtoGimbalActionPush
    _target = protocol.host2byte(4, 0)

    def __init__(self, pitch=0, yaw=0, pitch_speed=30, yaw_speed=30, coord=COORDINATE_YCPN, **kw):
        super().__init__(**kw)
        self._pitch = pitch
        self._yaw = yaw
        self._roll = 0
        self._pitch_speed = pitch_speed
        self._yaw_speed = yaw_speed
        self._coordinate = coord

    def __repr__(self):
        return "action_id:{0}, state:{1}, percent:{2}, pitch:{3}, yaw:{4}, roll:{5}, pitch_speed:{6}, yaw_speed:{7}, " \
               "coord:{8}".format(self._action_id, self._state, self._percent, self._pitch, self._yaw, self._roll,
                                  self._pitch_speed, self._yaw_speed, self._coordinate)

    def encode(self):
        proto = protocol.ProtoGimbalRotate()
        proto._pitch = self._pitch
        proto._yaw = self._yaw
        proto._pitch_speed = util.GIMBAL_PITCH_MOVE_SPEED_SET_CHECKER.val2proto(self._pitch_speed)
        proto._yaw_speed = util.GIMBAL_YAW_MOVE_SPEED_SET_CHECKER.val2proto(self._yaw_speed)
        proto._coordinate = self._coordinate
        return proto

    def update_from_push(self, proto):
        """ ??????????????????Action?????? """
        if proto.__class__ is not self._push_proto_cls:
            return

        self._percent = proto._percent
        if proto._action_state == 0:
            self._changeto_state(action.ACTION_RUNNING)
        elif proto._action_state == 1:
            self._changeto_state(action.ACTION_SUCCEEDED)
        elif proto._action_state == 2:
            self._changeto_state(action.ACTION_FAILED)
        elif proto._action_state == 3:
            self._changeto_state(action.ACTION_STARTED)
        else:
            logger.warning("GimbalMoveAction: update_from_push, unsupported state {0}".format(proto._action_state))
            return

        self._yaw = float(proto._yaw) / 10.0
        self._roll = float(proto._roll) / 10.0
        self._pitch = float(proto._pitch) / 10.0
        logger.info("{0}: update_from_push, {1}".format(self.__class__.__name__, self))


class GimbalRecenterAction(action.Action):
    _action_proto_cls = protocol.ProtoGimbalRecenter
    _push_proto_cls = protocol.ProtoGimbalActionPush
    _target = protocol.host2byte(4, 0)

    def __init__(self, pitch_speed=100, yaw_speed=100, **kw):
        super().__init__(**kw)
        self._pitch_valid = 1
        self._roll_valid = 0
        self._yaw_valid = 1
        self._yaw_speed = yaw_speed
        self._pitch_speed = pitch_speed
        self._roll_speed = 0
        self._yaw = 0
        self._pitch = 0
        self._roll = 0

    def __repr__(self):
        return "action_id:{0}, state:{1}, percent:{2}, pitch:{3}, yaw:{4}, roll:{5}, pitch_speed:{6}, " \
               "yaw_speed:{7}".format(self._action_id, self._state, self._percent, self._pitch, self._yaw,
                                      self._roll, self._pitch_speed, self._yaw_speed)

    def encode(self):
        proto = protocol.ProtoGimbalRecenter()
        proto._yaw_speed = self._yaw_speed
        proto._pitch_speed = self._pitch_speed
        return proto

    def update_from_push(self, proto):
        """ ??????????????????Action?????? """
        if proto.__class__ is not self._push_proto_cls:
            return

        self._percent = proto._percent
        self._update_action_state(proto._action_state)

        self._yaw = float(proto._yaw) / 10.0
        self._roll = float(proto._roll) / 10.0
        self._pitch = float(proto._pitch) / 10.0
        logger.info("GimbalRecenterAction, update_from_push {0}".format(self))


class GimbalPosSubject(dds.Subject):
    name = dds.DDS_GIMBAL_POS
    uid = dds.SUB_UID_MAP[name]
    type = dds.DDS_SUB_TYPE_PERIOD

    def __init__(self):
        self._yaw_angle = 0
        self._pitch_angle = 0
        self._yaw_ground_angle = 0
        self._pitch_ground_angle = 0
        self._option_mode = 0
        self._return_center = 0
        self._res = 0

    @property
    def angle(self):
        return self._pitch_angle, self._yaw_angle, self._pitch_ground_angle, self._yaw_ground_angle

    def data_info(self):
        return self._pitch_angle, self._yaw_angle, self._pitch_ground_angle, self._yaw_ground_angle

    def decode(self, buf):
        [self._yaw_ground_angle, self._pitch_ground_angle, self._yaw_angle,
         self._pitch_angle, self._res] = struct.unpack('<hhhhB', buf)
        self._return_center = (self._res >> 2) & 0x01
        self._option_mode = (self._res & 0x2)
        self._pitch_angle = util.GIMBAL_ATTI_PITCH_CHECKER.proto2val(self._pitch_angle)
        self._yaw_angle = util.GIMBAL_ATTI_YAW_CHECKER.proto2val(self._yaw_angle)
        self._pitch_ground_angle = util.GIMBAL_ATTI_PITCH_CHECKER.proto2val(self._pitch_ground_angle)
        self._yaw_ground_angle = util.GIMBAL_ATTI_YAW_CHECKER.proto2val(self._yaw_ground_angle)


class Gimbal(module.Module):
    """ EP ???????????? """

    _host = protocol.host2byte(4, 0)

    def __init__(self, robot):
        super().__init__(robot)
        self._action_dispatcher = robot.action_dispatcher

    # controls
    def suspend(self):
        """ ??????????????????????????????

        :return: bool:????????????
        """
        proto = protocol.ProtoGimbalCtrl()
        proto._order_code = 0x2ab5
        msg = protocol.Msg(self.client.hostbyte, self._host, proto)
        try:
            self.client.send_async_msg(msg)
            return True
        except Exception as e:
            logger.warning("Gimbal: suspend, send_async_msg exception {0}".format(str(e)))
            return False

    def resume(self):
        """ ????????????????????????????????????

        :return: bool:????????????
        """
        proto = protocol.ProtoGimbalCtrl()
        proto._order_code = 0x7ef2
        msg = protocol.Msg(self.client.hostbyte, self._host, proto)
        try:
            self.client.send_async_msg(msg)
            return True
        except Exception as e:
            logger.warning("Gimbal: resume, send_async_msg exception {0}".format(str(e)))
            return False

    def drive_speed(self, pitch_speed=30.0, yaw_speed=30.0):
        """ ???????????????????????????

        :param pitch_speed: float: [-360, 360]???pitch?????????????????? ??/s
        :param yaw_speed: float: [-360, 360]???yaw ?????????????????? ??/s

        :return: bool:????????????
        """
        proto = protocol.ProtoGimbalCtrlSpeed()
        proto._pitch_speed = util.GIMBAL_PITCH_SPEED_SET_CHECKER.val2proto(pitch_speed)
        proto._yaw_speed = util.GIMBAL_PITCH_SPEED_SET_CHECKER.val2proto(yaw_speed)
        return self._send_async_proto(proto)

    # actions
    def recenter(self, pitch_speed=60, yaw_speed=60):
        """ ??????????????????

        :param pitch_speed: float: [-360, 360]???pitch?????????????????? ??/s
        :param yaw_speed: float: [-360, 360]???yaw ?????????????????? ??/s

        :return: ??????action??????
        """
        action1 = GimbalRecenterAction(pitch_speed, yaw_speed)
        self._action_dispatcher.send_action(action1)
        return action1

    def _set_work_mode(self, mode):
        proto = protocol.ProtoGimbalSetWorkMode()
        proto._workmode = mode
        return self._send_sync_proto(proto)

    def move(self, pitch=0, yaw=0, pitch_speed=30, yaw_speed=30):
        """ ??????????????????????????????????????????????????????????????????

        :param pitch: float: [-55, 55]???pitch ?????????????????? ??
        :param yaw: float: [-55, 55]???yaw ?????????????????? ??
        :param pitch_speed: float: [0, 540]???pitch ???????????????????????? ??/s
        :param yaw_speed: float: [0, 540]???yaw ???????????????????????? ??/s
        :return: ??????action??????
        """
        pitch = util.GIMBAL_PITCH_MOVE_CHECKER.val2proto(pitch)
        yaw = util.GIMBAL_YAW_MOVE_CHECKER.val2proto(yaw)
        action1 = GimbalMoveAction(pitch, yaw, pitch_speed, yaw_speed, COORDINATE_CUR)
        self._action_dispatcher.send_action(action1)
        return action1

    def moveto(self, pitch=0, yaw=0, pitch_speed=30, yaw_speed=30):
        """ ??????????????????????????????????????????????????????????????????

        :param pitch: int: [-25, 30]???pitch ?????????????????? ??
        :param yaw: int: [-250, 250]???yaw ?????????????????? ??
        :param pitch_speed: int: [0, 540]???pitch ???????????????????????? ??
        :param yaw_speed: int: [0, 540]???yaw ???????????????????????? ??
        :return: ??????action??????
        """
        pitch = util.GIMBAL_PITCH_TARGET_CHECKER.val2proto(pitch)
        yaw = util.GIMBAL_YAW_TARGET_CHECKER.val2proto(yaw)
        action1 = GimbalMoveAction(pitch, yaw, pitch_speed, yaw_speed)
        self._action_dispatcher.send_action(action1)
        return action1

    # subscribes.
    def sub_angle(self, freq=5, callback=None, *args, **kw):
        """ ???????????????????????????

        :param freq: enum: (1, 5, 10, 20, 50) ???????????????????????????????????????????????? Hz
        :param callback: ??????????????????????????? (pitch_angle, yaw_angle, pitch_ground_angle, yaw_ground_angle):

                        :pitch_angle: ???????????????pitch?????????
                        :yaw_angle: ???????????????yaw?????????
                        :pitch_ground_angle: ????????????pitch?????????
                        :yaw_ground_angle: ????????????yaw?????????

        :param args: ????????????
        :param kw: ???????????????
        :return: bool: ??????????????????
        """
        sub = self._robot.dds
        subject = GimbalPosSubject()
        subject.freq = freq
        return sub.add_subject_info(subject, callback, args, kw)

    def unsub_angle(self):
        """ ???????????????????????????

        :return: bool: ???????????????????????????
        """
        sub_dds = self._robot.dds
        return sub_dds.del_subject_info(dds.DDS_GIMBAL_POS)
