from robomaster import robot
import time
from judge import Judge

def hit_callback(sub_info):
    # 被击打装甲的ID，被击打类型
    armor_id, hit_type = sub_info
    print("hit event: hit_comp:{0}, hit_type:{1}".format(armor_id, hit_type))

if __name__ == '__main__':
    ep_robot = robot.Robot()
    ep_robot.initialize(conn_type="sta")

    judge=Judge(ep_robot)
    judge.start()
    judge.sub_hit_event(hit_callback)
    print("Judge Version:",judge.__version__)
    while judge.deadflag==False:
        time.sleep(1)
        print(judge.hp)

    ep_robot.close()