from robomaster import robot

xSpeedP=0.8
xSpeedD=0.01
xLocalP=0.2


gimbal = 0

def gimbalInit(gimbalObj):
    global gimbal
    gimbal = gimbalObj
    gimbalObj.resume()


last_yErr=0
last_xErr=0
def aim(targetPt):
    global last_xErr
    global gimbal
    centX = 320 / 2
    centY = 180 / 2
    xErr = targetPt[0]-centX
    yErr = -(targetPt[1]-centY)
    delta_xErr = xErr - last_xErr
    delta_yErr = yErr - last_yErr
    xSpeed=abs(xErr)*xSpeedP+(delta_xErr*xSpeedD)
    ySpeed=abs(yErr)*xSpeedP+(delta_yErr*xSpeedD)
    yawAngle=xErr*xLocalP
    pitchAngle=yErr*xLocalP
    if abs(pitchAngle)>0.1 or abs(yawAngle)>0.1:
        print("cmds:", pitchAngle, yawAngle, ySpeed, xSpeed)
        gimbal.move(pitchAngle,yawAngle,ySpeed,xSpeed).wait_for_completed()




