# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 按两次 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import time
import robomaster
from robomaster import robot
from robomaster import led


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    print_hi('PyCharm')
   # robomaster.config.LOCAL_IP_STR = "192.168.10.22"
    tt_drone=robot.Drone()
   #SDK说明文档中缺乏关于initialize的说明
    tt_drone.initialize()
    tl_sn=tt_drone.get_sn()
    #tt_drone.led.set_mled_char(color='b', display_char='C')
    tt_drone.led.set_mled_char(color='b',display_char='C')
    time.sleep(0.5)
    tt_drone.led.set_mled_char(color='r', display_char='B')
    time.sleep(0.5)
    tt_drone.close()


# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
