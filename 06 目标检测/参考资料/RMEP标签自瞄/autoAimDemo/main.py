import sys
import time
from robomaster import robot
import cv2
import numpy as np

import connHelper
import signReco
import aim

pitchAngle=0
yawAngle=0
targetPoint=[0,0]
aimFlag=True
targetFlag=False
def gimbalCallback(args):
    global pitchAngle
    global yawAngle
    global targetPoint
    #print(args)
    pitchAngle=args[0]
    yawAngle=args[1]
    if targetFlag and aimFlag:
        aim.aim(targetPoint)

if __name__ == '__main__':
    #if connHelper.start(ssid="Xiaomi_CC65OT", password="435782572") == False:
    #    sys.exit()
    time.sleep(1)
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta")
    ep_camera = ep_robot.camera
    ep_gimbal = ep_robot.gimbal
    aim.gimbalInit(ep_gimbal)
    ep_gimbal.sub_angle(freq=5, callback=gimbalCallback)

    # 每次获取最新的1帧图像显示，并停留1秒
    ep_camera.start_video_stream(display=False)
    while True:
        try:
            # 读入数字模板
            for i in range(1, 4):
                signReco.Templates[i] = np.load('./' + str(i) + '.npy')
                # 读入图像
            img = ep_camera.read_cv2_image(strategy="newest")
            img = cv2.resize(img, (320, 180))
            # cv2.imshow('RoboMaster EP Vedio',img)
            imgT = img.copy()
            cx = int(imgT.shape[1] / 2 - 30)
            cy = int(imgT.shape[0] / 2)
            # 目标搜索
            ret, targetPt, contour = signReco.findTarget(img)
            if ret == False:
                cv2.putText(imgT, 'No Target!', (cx, cy), cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 1, 8, 0);
                targetFlag = False
            else:
                # 绘制外接矩形
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(imgT, (x, y), (x + w, y + h), (0, 255, 0), 1)
                # 目标识别
                ret, num = signReco.objectIdentify(img, contour)
                if ret:
                    text = str(num)
                    # 瞄准
                    targetPoint = targetPt
                    targetFlag=True
                else:
                    targetPoint = targetPt
                    targetFlag=True
                    text = 'Unidentified'
                cv2.putText(imgT, text, (targetPt[0] + 10, targetPt[1]), \
                            cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 1, 8, 0);
                cv2.circle(imgT, targetPt, 1, (0, 0, 255), 2)  # 画红点
                text = "(" + str(targetPt[0]) + ", " + str(targetPt[1]) + ")"
                cv2.putText(imgT, text, (targetPt[0] + 10, targetPt[1] + 10), \
                            cv2.FONT_HERSHEY_PLAIN, 0.7, (0, 0, 255), 1, 8, 0);


            # 显示
            cv2.imshow('RoboMaster EP Vedio', imgT)
            cv2.waitKey(1)

        except KeyboardInterrupt:
            ep_camera.stop_video_stream()
            ep_robot.close()
            print('User Interrupt')
            cv2.destroyAllWindows()
            break

    print('quit')
    sys.exit()


