from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.http import Http404
from django.template.response import TemplateResponse
from django.views import View

from daka.core import test_login
from daka.models import Task, Log


class QueryView(View):
    def get(self, request):
        user_name = request.GET.get('user_name', None)
        try:
            task = Task.objects.get(user_name=user_name)
        except Task.DoesNotExist:
            raise Http404
        return TemplateResponse(request, 'query.html', {
            'task': task,
            'logs': Log.objects.filter(task=task).order_by('-created', '-id')[:100].all()
        })


class WhoView(View):
    def get(self, request):
        return TemplateResponse(request, 'who.html', {
            'tasks': Task.objects.all()
        })


class MainView(View):
    def get(self, request):
        return TemplateResponse(request, 'main.html')

    def post(self, request):
        form = ReserveForm(request.POST)
        if not form.is_valid():
            return TemplateResponse(request, 'main.html', {
                'error': form.errors
            })
        form.save()
        return TemplateResponse(request, 'main.html', {
            'error': '注册成功'
        })


class ReserveForm(ModelForm):
    class Meta:
        model = Task
        fields = ('user_name', 'password')
        error_messages = {
            'user_name': {
                'required': '学号不能为空',
                'unique': '该学号已经被注册'
            },
            'password': {
                'required': '密码不能为空'
            }
        }

    def clean(self):
        super().clean()
        if not test_login(self.data.get('user_name', ''), self.data.get('password', '')):
            raise ValidationError('学号或密码不正确')
