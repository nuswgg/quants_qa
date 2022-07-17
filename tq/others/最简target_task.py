from tqsdk import TqApi, TqAuth, TargetPosTask
import time

api = TqApi(auth=TqAuth("xxxx", "xxxx"))

quote = api.get_quote('CFFEX.IH2207')

his_position = 3
task_exist = 0

while True:
    api.wait_update(time.time() + 1)
    # 无任务且有昨仓
    if task_exist == 0 and his_position > 0:
        print("任务1")
        task_his = TargetPosTask(api, symbol='CFFEX.IH2207', price="ACTIVE",
                                 min_volume=1, max_volume=3,
                                 offset_priority='昨,开')
        his_position = 0
        task_exist = 1
    # 无任务且无昨仓
    elif task_exist == 0 and his_position == 0:
        print("任务2")
        task_today = TargetPosTask(api, symbol='CFFEX.IH2207', price="ACTIVE",
                                   min_volume=1, max_volume=3,
                                   offset_priority='开')
        his_position = 3
        task_exist = 2

    # 有任务且有昨仓
    elif task_exist == 1:
        task_his.cancel()
        print("撤销1")
        while task_his.is_finished():
            print("撤销成功1")
            task_exist = 0
            break
    # 有任务且无昨仓
    elif task_exist == 2:
        task_today.cancel()
        print("撤销2")
        while task_today.is_finished():
            print("撤销成功2")
            task_exist = 0
            break

