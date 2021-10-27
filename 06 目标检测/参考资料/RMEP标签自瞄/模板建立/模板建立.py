import numpy as np
import cv2 as cv
#读取文件 阈值化
num=1
img = cv.imread('./img/num'+ str(num) +'.png')
imge=cv.resize(img,(98,98))
ROIhsv=cv.cvtColor(imge,cv.COLOR_BGR2HSV)
lower_red = np.array([0,200,0])
upper_red = np.array([255,255,255])
ROImask = cv.inRange(ROIhsv, lower_red, upper_red)
#制作模板并保存
form=np.zeros((7,7), dtype=int)
for i in range(7):
    for j in range(7):
        x=i*14
        y=j*14
        subMask=ROImask[y:y+14,x:x+14]
        sumVal=subMask.sum()/255
        if sumVal<80.0:#黑
            form[j,i]=1
np.save('./'+str(num)+'.npy',form)
#读取模板并显示
n=np.load('./'+str(num)+'.npy')
print(n)
