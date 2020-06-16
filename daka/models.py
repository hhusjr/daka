from django.db import models


class Task(models.Model):
    user_name = models.CharField(verbose_name='用户名', max_length=32, unique=True)
    password = models.CharField(verbose_name='密码', max_length=128)
    created = models.DateTimeField(verbose_name='注册时间', auto_now_add=True)
    daka_time = models.DateTimeField(verbose_name='最后一次打卡时间', null=True, blank=True)

    def __str__(self):
        return 'Task [{}]'.format(self.user_name)


class Log(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='对应任务')
    message = models.TextField(verbose_name='消息')
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
