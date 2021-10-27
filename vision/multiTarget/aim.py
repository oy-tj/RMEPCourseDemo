from robomaster import robot
from robomaster import blaster

xSpeedP=0.8
xSpeedD=0.01
xLocalP=0.2


gimbal = 0
_blaster= 0


def gimbalInit(gimbalObj,blasterObj):
    global gimbal,_blaster
    gimbal = gimbalObj
    gimbalObj.resume()
    _blaster=blasterObj


last_yErr=0
last_xErr=0
def aim(targetPt,yOffset=-5,fire_type=blaster.WATER_FIRE):
    global last_xErr
    global gimbal
    centX = 320 / 2
    centY = 180 / 2
    xErr = targetPt[0]-centX
    yErr = -(targetPt[1]+yOffset-centY)
    delta_xErr = xErr - last_xErr
    delta_yErr = yErr - last_yErr
    xSpeed=abs(xErr)*xSpeedP+(delta_xErr*xSpeedD)
    ySpeed=abs(yErr)*xSpeedP+(delta_yErr*xSpeedD)
    yawAngle=xErr*xLocalP
    pitchAngle=yErr*xLocalP
    if abs(pitchAngle)>0.2 or abs(yawAngle)>0.2:
        print("cmds:", pitchAngle, yawAngle, ySpeed, xSpeed)
        gimbal.move(pitchAngle,yawAngle,ySpeed,xSpeed).wait_for_completed()
    else:
        _blaster.fire(fire_type=fire_type,times=1)





