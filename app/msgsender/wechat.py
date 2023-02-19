import itchat
import json
from apscheduler.schedulers.blocking import BlockingScheduler

def auto_send(msg, toUser):
    itchat.send(msg=msg, toUserName=toUser)

if __name__ == "__main__":
    itchat.login()
    itchat.auto_login(hotReload=True)
    #获取好友列表
    friends = itchat.get_friends()
    #转换为字典
    friendsStr = json.dumps(friends)
    print(friendsStr)
    #发送消息
    itchat.send(msg="你好", toUserName="")

    # try:
    #     for item in friends:
    #         if(item["NickName"] == "安静"):
    #             toUser = item["UserName"]
    #         scheduler = BlockingScheduler()
    #         scheduler.add_job(auto_send, "cron", day_of_week="0-6", hour=15, minute=17, args=["你好", toUser])
    #         scheduler.start()
    #         itchat.run()
    # except Exception as ex:
    #     itchat.logout()
    #     print(ex)