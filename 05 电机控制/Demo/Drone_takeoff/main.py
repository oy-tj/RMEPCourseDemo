# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 按两次 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import robomaster
from robomaster import robot
import time

def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('xmu')
    tl_drone=robot.Drone()
    #robomaster.config.LOCAL_IP_STR = "192.168.10.22"
    tl_drone.initialize()
    tl_drone_sn=tl_drone.get_sn()
    tl_drone_bat=tl_drone.battery
    tl_drone_bat_in=tl_drone_bat.get_battery()
    print("电池电量为：",tl_drone_bat_in)

    tl_drone_tem = tl_drone.get_temp()
    print("飞机当前温度低温是：",tl_drone_tem)
    time.sleep(0.5)

    tl_led=tl_drone.led
    tl_led.set_mled_char(color='b', display_char='1')

    tl_flight=tl_drone.flight
    tl_flight.takeoff().wait_for_completed()
    tl_led.set_mled_char(color='b', display_char='2')
    time.sleep(1)
    tl_flight.forward(distance=30).wait_for_completed()
    tl_led.set_mled_char(color='b', display_char='3')
    time.sleep(1)
    tl_flight.backward(distance=30).wait_for_completed()
    tl_led.set_mled_char(color='b', display_char='4')
    time.sleep(1)

    tl_flight.land().wati_for_completed()
    tl_led.set_mled_char(color='b', display_char='5')
    tl_drone.close()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
