import time
import robomaster
from robomaster import conn
from MyQR import myqr
from PIL import Image


def start(ssid, password):
    QRCODE_NAME = "qrcode.png"
    helper = conn.ConnectionHelper()
    info = helper.build_qrcode_string(ssid=ssid, password=password)
    myqr.run(words=info)
    time.sleep(1)
    img = Image.open(QRCODE_NAME)
    img.show()
    if helper.wait_for_connection():
        print("Connected!")
        return True
    else:
        print("Connect failed!")
        return False
