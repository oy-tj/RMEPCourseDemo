import time
import robomaster
from robomaster import robot
from robomaster import led
import math

class Judge:
    def __init__(self,ep_robot):
        self.__version__="0.0.1"
        #实例化对象
        self.ep_robot=ep_robot
        self.ep_led = ep_robot.led
        self.ep_armor = ep_robot.armor
        #初始化LED
        self.r=0
        self.g=25
        self.b=255
        #全红
        self.ep_led.set_gimbal_led(comp='top_all', r=255, g=0, b=0, 
                                        led_list=range(8), effect='on')
        self.ep_led.set_led(comp="bottom_all",  r=255, g=0, b=0, effect='on')
        time.sleep(0.5)
        #全灭
        self.ep_led.set_gimbal_led(comp='top_all', r=self.r, g=self.g, b=self.b, 
                                        led_list=range(8), effect='off')
        self.ep_led.set_led(comp="bottom_all",  r=self.r, g=self.g, b=self.b, effect='off')
        time.sleep(0.5)
        #初始化血量
        self.hp=80
        self._hp2led()
        #self._subflag=False
        self._sub_callback=None
        self.deadflag=False
    
    #根据血量显示LED
    def _hp2led(self):
        led_num=math.ceil(self.hp/10)
        self.ep_led.set_gimbal_led(comp='top_all', r=self.r, g=self.g, b=self.b, 
                                        led_list=range(led_num), effect='on')
        
        self.ep_led.set_led(comp="bottom_all",  r=self.r, g=self.g, b=self.b, effect='on')

    #启动打击检测
    def start(self):
        #启动打击检测
        # 设置所有装甲灵敏度为 2，[0-10]系数越大灵敏度越低
        self.ep_armor.set_hit_sensitivity(comp="all", sensitivity=2)
        # 订阅装甲被击打的事件
        self.ep_armor.sub_hit_event(self._hit_callback)
        print("Judgment System Start Up!")

    #停止打击检测
    def stop(self) :
        self.ep_armor.unsub_hit_event()
        #全红
        self.ep_led.set_gimbal_led(comp='top_all', r=255, g=0, b=0, led_list=range(8), effect='on')
        self.ep_led.set_led(comp="bottom_all",  r=255, g=0, b=0, effect='on')
        self.ep_robot.close()
        self.deadflag=True
        print("Judgment System Shut down!")


    #用户订阅打击数据
    def sub_hit_event(self,callback):
        self._sub_callback = callback
    def unsub_hit_event(self,callback):
        self._sub_callback = None

    #打击回调函数
    def _hit_callback(self,sub_info):
        #全灭
        self.ep_led.set_gimbal_led(comp='top_all', r=0, g=0, b=0, 
                                        led_list=range(8), effect='off')
        self.ep_led.set_led(comp="bottom_all",  r=self.r, g=self.g, b=self.b, effect='off')
        if self._sub_callback != None:
            self._sub_callback(sub_info)
        self.hp-=10
        #armor_id, hit_type = sub_info
        #print("hit event: hit_comp:{0}, hit_type:{1}，hp:{2}".format(armor_id, hit_type,self.hp))
        self._hp2led()
        if self.hp<=0:
            self.stop()
    

        

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta")

    judge=Judge(ep_robot)
    judge.start()
    while True:
        time.sleep(0.1)

    ep_robot.close()