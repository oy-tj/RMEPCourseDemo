import cv2 as cv
import numpy as np

DEBUG = True


# 1.HSV阈值化
# lower、upper是HSV值的上下限，列表格式[h,s,v]
def hsvThreshold(BGRImg, lower, upper):
    hsvimg = cv.cvtColor(BGRImg, cv.COLOR_BGR2HSV)
    lower_ = np.array(lower)
    upper_ = np.array(upper)
    mask = cv.inRange(hsvimg, lower_, upper_)
    return mask


# 2.搜索目标
def findTarget(img):
    # 阈值化
    mask = hsvThreshold(img, [0, 190, 60], [15, 255, 220])  # HSV阈值化，此处注意调参
    mask1 = hsvThreshold(img, [140, 190, 60], [180, 255, 220])
    mask = mask + mask1
    global DEBUG
    if DEBUG:
        cv.imshow('hsvThreshold', mask)
    hsvimg = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    if DEBUG:
        cv.imshow('HSV', hsvimg)
    # 形态学处理
    kernel = np.ones((3, 3), np.uint8)
    mask = cv.erode(mask, kernel, iterations=1)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv.dilate(mask, kernel, iterations=1)
    # img=cv.cvtColor(img,cv.COLOR_BGR2RGB)
    # img=Image.fromarray(np.uint8(img))
    # 轮廓检测
    contours, hierarchy = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    max_area = 0
    max_area_id = 999
    for i in range(len(contours)):
        area = cv.contourArea(contours[i])
        if area > max_area:
            max_area = area
            max_area_id = i
    if max_area_id == 999:
        return False, 0, 0
    # 凸包补齐轮廓
    hull = cv.convexHull(contours[max_area_id])  # 计算凸包
    area = cv.contourArea(hull)
    if area / mask.size > 0.005:  # 目标足够大
        mom = cv.moments(hull)
        pt = (int(mom['m10'] / mom['m00']), int(mom['m01'] / mom['m00']))  # 使用前三个矩m00, m01和m10计算重心
    else:
        return False, 0, 0
    return True, pt, hull


# 3.识别目标
# 3.1输入四边形的四个顶点和要寻找象限，返回在象限的那个顶点的float类型坐标列表
def pointInQuadrant(pointSet):
    dt = np.dtype([('x', int), ('y', int)])
    pSet = np.array([tuple(pointSet[0]), tuple(pointSet[1]), tuple(pointSet[2]), tuple(pointSet[3])], dtype=dt)
    x_index_order = np.argsort(pSet, order='x')
    x_index_order = np.argsort(x_index_order)
    y_index_order = np.argsort(pSet, order='y')
    y_index_order = np.argsort(y_index_order)
    # print(pSet,x_index_order,y_index_order)
    Quadrant = [0, 0, 0, 0]
    for i in range(4):
        x = x_index_order[i]
        y = y_index_order[i]
        if x >= 2 and y < 2:
            Quadrant[i] = 0
        elif x < 2 and y < 2:
            Quadrant[i] = 1
        elif x < 2 and y >= 2:
            Quadrant[i] = 2
        elif x >= 2 and y >= 2:
            Quadrant[i] = 3
    Quadrant = np.argsort(Quadrant)
    # print(Quadrant,qqq)
    return [pointSet[Quadrant[0]], pointSet[Quadrant[1]], pointSet[Quadrant[2]], pointSet[Quadrant[3]]]


# Templates=''
Templates = list(range(10))
# 3.2与现有模板比对，结果越小越接近
def cmpTemplate(grid, num):
    global Templates
    template = Templates[num]
    if type(template) == type(1):
        return 99
    # print(grid,'\n',template,'\n','\n')
    m = grid - template
    m = m.reshape(m.size)
    # 计算两个矩阵差的1范数
    # （矩阵相减后对每个元素的绝对值进行累加
    # ，结果越小，两个矩阵越相似）
    return np.linalg.norm(m, ord=1)


# 3.3目标识别
def objectIdentify(img, targetContour):
    # 拟合四边形
    T = 0.001
    approx = range(10)
    while len(approx) > 4:
        epsilon = T * cv.arcLength(targetContour, True)
        approx = cv.approxPolyDP(targetContour, epsilon, True)
        T += 0.001
    if len(approx) != 4:
        return False, 0
    # 仿射变换，四边形->正方形
    pointSet = [approx[0, 0], approx[1, 0], approx[2, 0], approx[3, 0]]
    pts1 = np.float32(pointInQuadrant(pointSet))
    pts2 = np.float32([[198, 50], [100, 50], [100, 148], [198, 148]])
    M = cv.getPerspectiveTransform(pts1, pts2)  # 获取变化矩阵Tmplates
    imgT = img.copy()
    dst = cv.warpPerspective(imgT, M, (img.shape[1], img.shape[0]))  # 仿射变换
    ROI = dst[50:148, 100:198]
    # HSV阈值化
    ROIhsv = cv.cvtColor(ROI, cv.COLOR_BGR2HSV)
    ROImask = hsvThreshold(ROIhsv, [15, 0, 0], [140, 255, 255])  # HSV阈值化，此处注意调参，这里的参数可以更苛刻
    ROImask1 = hsvThreshold(ROIhsv, [140, 0, 30], [180, 255, 180])
    ROImask += ROImask1
    # disImg(ROI,ROImask)##########################
    # 栅格化（rasterization）
    grid = np.zeros((7, 7), dtype=int)
    for i in range(7):
        for j in range(7):
            x = i * 14
            y = j * 14
            subMask = ROImask[y:y + 14, x:x + 14]
            sumVal = subMask.sum() / 255
            if sumVal < 80.0:  # 黑
                grid[j, i] = 1
    # print( grid)##############################
    # 模板比对
    matching = np.array([99 for x in range(0, 10)])
    for i in range(10):
        matching[i] = cmpTemplate(grid, i)
    mIndex = np.argsort(matching)[0]
    # print(matching)
    if (matching[mIndex] > 2):
        return False, mIndex
    else:
        return True, mIndex
