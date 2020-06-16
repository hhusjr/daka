import datetime
import time

from django.db.models import Q

from daka.apps import DakaConfig
from daka.core import DakaDFA
from daka.models import Task, Log


def save_log(message, task):
    Log.objects.create(task=task, message=message)


def run_daka():
    current_time = datetime.datetime.now()
    start_time = datetime.datetime(hour=DakaConfig.daka_start_time[0], minute=DakaConfig.daka_start_time[1], second=0,
                                   year=current_time.year, month=current_time.month, day=current_time.day)
    end_time = datetime.datetime(hour=DakaConfig.daka_end_time[0], minute=DakaConfig.daka_end_time[1], second=0,
                                 year=current_time.year, month=current_time.month, day=current_time.day)
    if current_time < start_time or current_time > end_time:
        print('Time not in range, exiting...')
        return

    for task in Task.objects.filter(Q(daka_time=None) | Q(daka_time__lt=start_time)):
        daka = DakaDFA(task.user_name, task.password)
        is_success, _ = daka.run(lambda message: save_log(message, task))

        if is_success:
            print('{}打卡成功'.format(task.user_name))
            # send_mail('打卡成功提醒', '您好，您{}的健康上报打卡成功啦！'.format(current_time), DEFAULT_FROM_EMAIL,
            #         [task.email])
            task.daka_time = datetime.datetime.now()
            task.save()

        time.sleep(0.5)

    print('Task finished, exiting...')
