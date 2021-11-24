import time
import keyboard

staName = ['Initialize', 'S1', 'S2']
sta = 0
cnt = 0

def changeSta():
    global cnt
    cnt = 0
    print()

def printProgress():
    global cnt, sta, staName
    cnt += 1
    print('\rSTATE %d %s:[%d/%d]' % (sta, staName[sta],  cnt, 100), end='  ')
    if cnt == 100:
        sta += 1
        changeSta()
    time.sleep(0.1)


if __name__ == '__main__':
    print("以两种方式遍历staName列表")
    for s in staName:
        print(s)
    for i in range(len(staName)):
        print(i,':',staName[i])
    while sta == 0:
        printProgress()
    while True:
        while sta == 1:
            printProgress()
            if keyboard.is_pressed('2'):  # if key '2' is pressed
                sta = 2
                changeSta()
        while sta == 2:
            printProgress()
            if keyboard.is_pressed('1'):  # if key '1' is pressed
                sta = 1
                changeSta()
        if sta == 3:
            print('Quit')
            break