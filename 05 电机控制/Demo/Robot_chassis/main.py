# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 按两次 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import robomaster
from robomaster import robot
import time

def sub_info_handler(batter_info, ep_robot):
    percent = batter_info
    print("电池电量: {0}%.".format(percent))
   # ep_led = ep_robot.led
   # brightness = int(percent * 255 / 100)
   # ep_led.set_led(comp="all", r=brightness, g=brightness, b=brightness)

def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('xmu_robot')
    ep_robot=robot.Robot()
    ep_robot.initialize(conn_type='sta')

    ep_battery = ep_robot.battery
    ep_battery.sub_battery_info(5, sub_info_handler, ep_robot)

    ep_led=ep_robot.led
    ep_led.set_led(comp='all', effect='off')
    time.sleep(0.1)
    ep_chassis=ep_robot.chassis
    ep_led.set_led(comp='bottom_back', r=255, g=0, b=0, effect='on')
    time.sleep(0.5)
    ep_chassis.move(x=0.8, y=0, z=0, xy_speed=0.7).wait_for_completed()
    time.sleep(4)
    ep_led.set_led(comp='all', effect='off')

    ep_led.set_led(comp='bottom_back', r=0, g=255, b=0, effect='on')
    time.sleep(0.5)
    ep_chassis.move(x=-0.8, y=0, z=0, xy_speed=0.7).wait_for_completed()
    ep_battery.unsub_battery_info()
    ep_robot.close()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
