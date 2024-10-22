from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import Day, User, ToDo, JobPatternForOperators, ExtraTask
from . import schedule_utils as sc
from django.core.exceptions import ObjectDoesNotExist
import datetime


class EditSchedule(View):
    template: str = 'edit_day.html'

    context = {'date': None, 'date_name': '', 'comment': '', 'current_worker': '', 'users': []}
    users = User.objects.all()
    today = datetime.date.today()
    powder_weekday = 'Четверг'
    optics_weekday = 'Пятница'
    # today = datetime.date(2024, 9, 12)

    for user in users:
        context['users'].append(user)


    def get(self, request, id=None):
        d = Day.objects.get(date=id)

        self.context['date'] = id

        month = int(id.split('-')[1])
        day = int(id.split('-')[2])
        month_name = sc.months_list[month - 1]
        self.context['date_name'] = f'{month_name}, {day}'

        # self.context['jobs'] = [task.task for task in ExtraTask.objects.filter(date=d)]
        self.context['jobs'] = []
        for job in JobPatternForOperators.objects.all():
            j = {'name': job.name}
            if job.name not in sc.tasks_list:
                try:
                    done = ToDo.objects.get(task=job, date=d)
                    j['times'] = done.times
                except ObjectDoesNotExist:
                    j['times'] = 0
                self.context['jobs'].append(j)
            else:
                if job.name == 'Взвешивание порошка' and d.weekday == self.powder_weekday:
                    try:
                        done = ToDo.objects.get(task=job, date=d)
                        j['times'] = done.times
                    except ObjectDoesNotExist:
                        j['times'] = 0
                    self.context['jobs'].append(j)

                elif job.name == 'Очистка оптики' and d.weekday == self.optics_weekday:
                    try:
                        done = ToDo.objects.get(task=job, date=d)
                        j['times'] = done.times
                    except ObjectDoesNotExist:
                        j['times'] = 0
                    self.context['jobs'].append(j)

                elif job.name == 'Чистка установок' and day == 1:
                    try:
                        done = ToDo.objects.get(task=job, date=d)
                        j['times'] = done.times
                    except ObjectDoesNotExist:
                        j['times'] = 0
                    self.context['jobs'].append(j)

                elif day <= 3 and d.weekday == 'Суббота' and job.name == 'Чистка установок':
                    try:
                        done = ToDo.objects.get(task=job, date=d)
                        j['times'] = done.times
                    except ObjectDoesNotExist:
                        j['times'] = 0
                    self.context['jobs'].append(j)

                elif day == 28 and job.name == 'Очистка циклона':
                    try:
                        done = ToDo.objects.get(task=job, date=d)
                        j['times'] = done.times
                    except ObjectDoesNotExist:
                        j['times'] = 0
                    self.context['jobs'].append(j)

                elif 26 <= day < 28 and d.weekday == 'Среда' and job.name == 'Очистка циклона':
                    try:
                        done = ToDo.objects.get(task=job, date=d)
                        j['times'] = done.times
                    except ObjectDoesNotExist:
                        j['times'] = 0
                    self.context['jobs'].append(j)

        self.context['comment'] = d.comment
        try:
            self.context['current_worker'] = d.user.all()[0]
        except IndexError:
            self.context['current_worker'] = ''

        self.context['extra_tasks'] = ExtraTask.objects.filter(date=d)

        return render(request, self.template, self.context)

    def post(self, request, id=None):
        day = Day.objects.get(date=id)

        if 'back' in request.POST:
            return redirect(f'/mycalendar')

        if 'new_task' in request.POST:
            return redirect(f'{id}/extra_task')

        if 'id' in request.POST:
            print(request.POST)
            attr = request.POST['id']
            value = request.POST['value']
            if 'task' in request.POST:
                task = JobPatternForOperators.objects.get(name=request.POST['task'])
                try:
                    todo = ToDo.objects.get(task=task, date=day)
                except ObjectDoesNotExist:
                    todo = ToDo.objects.create(task=task, date=day)
                finally:
                    if int(value) == 0:
                        todo.delete()
                    else:
                        todo.times = int(value)
                        todo.save()
            elif attr == 'user':
                user = User.objects.get(name=value)
                day.user.clear()
                day.user.add(user)
                day.edited = True
                day.save()
            elif attr == 'extra_ready':
                extra_task = ExtraTask.objects.get(task=request.POST['job'],
                                                   date=day)
                extra_task.done = request.POST['value']
                extra_task.save()
            else:
                setattr(day, attr, value)
                day.edited = True
                day.save()
        return render(request, self.template, self.context)