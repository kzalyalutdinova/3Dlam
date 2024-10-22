import calendar

from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views import View
from .models import User, Powder, Day, ToDo, ExtraTask
import datetime
from . import schedule_utils as sc
from .HTML_Calendar import WorkCalendar
from django.http import JsonResponse



class CreateSchedule(View):
    template: str = '2_home_page.html'
    date = str(datetime.date.today()).split('-')
    year = int(date[0])
    month = int(date[1])
    month_name = sc.months_list[month - 1]
    first_weekday = int(datetime.date(year=year, month=month, day=1).weekday())
    users = User.objects.all()
    http_methods_names = ['get', 'post']
    o_day = 27
    y_day = 0
    powder_day = []
    optics_day = []
    cyclone_day = None
    cleaning_day = None


    def update_date(self, date):
        self.date = date.split('-')
        self.month = int(self.date[1])
        self.year = int(self.date[0])
        self.month_name = sc.months_list[self.month - 1]
        self.first_weekday = int(datetime.date(year=self.year, month=self.month, day=1).weekday())

    def set_workers(self, day, instance, shift):
        """
        :param day: int
        :param instance: models.Day object
        :return: None
        """
        for worker in range(len(self.users)):
            # print(self.users)
            # print(f'Shift+worker: {(shift + worker) % 4}, {(day + 1) % 4}')
            if (shift + worker) % 4 == (day + 1) % 4:
                worker_obj = self.users[worker]
                # print(worker_obj.name)
                instance.user.add(worker_obj)

    def update_tasks(self):
        y_weekday_num = calendar.weekday(self.year, self.month, self.y_day + 1)
        o_weekday_num = calendar.weekday(self.year, self.month, self.o_day + 1)
        if o_weekday_num == 3:
            self.o_day -= 1
        elif o_weekday_num == 4:
            self.o_day -= 2

        if y_weekday_num == 3:
            self.y_day += 2
        elif y_weekday_num == 4:
            self.y_day += 1

    def get(self, request):
        if 'id' in request.GET:
            date = Day.objects.get(date=datetime.date(year=int(request.GET['id'].split('-')[0]),
                                                      month=int(request.GET['id'].split('-')[1]),
                                                      day=int(request.GET['id'].split('-')[2])))
            tasks = [item.task.name for item in ToDo.objects.filter(date=date)]
            tasks.extend([item.task for item in ExtraTask.objects.filter(date=date, done=True)])
            return JsonResponse({'tasks':tasks, 'date':request.GET['id']})

        shift = sc.count_shift(self.month, self.year)
        month_year_obj = sc.get_or_create_MonthYear(obj_name=f'{self.month_name}-{self.year}',
                                                    shift=shift,
                                                    month_num=self.month,
                                                    year=self.year)

        self.update_tasks()
        for day in range(month_year_obj.days_amount):
            weekday = sc.weekdays_list[(self.first_weekday + day) % 7]
            date = f'{self.year}-{self.month}-{day + 1}'
            # print(date, weekday)
            instance = sc.get_or_create_day(date=date, weekday=weekday, month_year=month_year_obj)

            if not instance.edited:
                # print(instance.date)
                self.set_workers(day=day, instance=instance, shift=shift)


            task = sc.set_tasks(weekday=instance.weekday, day_num=day, o_day=self.o_day, y_day=self.y_day)

            if task == 'powder day':
                self.powder_day.append(instance.date)

            elif task == 'cleanup day':
                self.optics_day.append(instance.date)

            elif task == 'cyclone day':
                self.cyclone_day = instance.date

            elif task == 'cleaning day':
                self.cleaning_day = instance.date



        cal = WorkCalendar()
        html_calendar = cal.formatmonth(self.year, self.month, withyear=True)
        html_calendar = html_calendar.replace('<td ', '<td  width="150" height="150"')

        for d in self.powder_day:
            html_calendar = html_calendar.replace(f'id="{d}"', f'id="{d}" name="powder_day"')
        for d in self.optics_day:
            html_calendar = html_calendar.replace(f'id="{d}"', f'id="{d}" name="optics_day"')

        html_calendar = html_calendar.replace(f'id="{self.cyclone_day}"',
                                              f'id="{self.cyclone_day}" name="cyclone_day"')
        html_calendar = html_calendar.replace(f'id="{self.cleaning_day}"',
                                              f'id="{self.cleaning_day}" name="cleaning_day"')
        context = {'html_calendar': mark_safe(html_calendar),
                   'month': self.month,
                   'year': self.year,
                   'powders': Powder.objects.all()}
        # print(mark_safe(html_calendar))
        return render(request, self.template, context)

    def post(self, request):

        if 'next-month' in request.POST:
            if request.POST['current-month'] == '':
                current_month = self.month
                current_year = self.year
            else:
                current_month = int(request.POST['current-month'])
                current_year = int(request.POST['current-year'])
            next_month, year = sc.show_nextMonth(current_month, current_year)
            date = str(datetime.date(year=year, month=next_month, day=1))
            self.update_date(date)

        elif 'previous-month' in request.POST:
            if request.POST['current-month'] == '':
                current_month = self.month
                current_year = self.year
            else:
                current_month = int(request.POST['current-month'])
                current_year = int(request.POST['current-year'])
            next_month, year = sc.show_prevMonth(current_month, current_year)
            date = str(datetime.date(year=year, month=next_month, day=1))
            self.update_date(date)
        elif 'redirect-to-table' in request.POST:
            return redirect('material_table')

        shift = sc.count_shift(self.month, self.year)
        month_year_obj = sc.get_or_create_MonthYear(obj_name=f'{self.month_name}-{self.year}',
                                                    shift=shift,
                                                    month_num=self.month,
                                                    year=self.year)

        self.update_tasks()
        for day in range(month_year_obj.days_amount):
            weekday = sc.weekdays_list[(self.first_weekday + day) % 7]
            date = f'{self.year}-{self.month}-{day + 1}'
            # print(date, weekday)
            instance = sc.get_or_create_day(date=date, weekday=weekday, month_year=month_year_obj)
            # print(instance.date)
            if not instance.edited:
                self.set_workers(day=day, instance=instance, shift=shift)
            task = sc.set_tasks(weekday=instance.weekday, day_num=day, o_day=self.o_day, y_day=self.y_day)

            if task == 'powder day':
                self.powder_day.append(instance.date)

            elif task == 'cleanup day':
                self.optics_day.append(instance.date)

            elif task == 'cyclone day':
                self.cyclone_day = instance.date

            elif task == 'cleaning day':
                self.cleaning_day = instance.date


        if all(x in request.POST for x in ['printer', 'material', 'height']):
            result = round(float(request.POST['height'])
                           * float(request.POST['printer'])
                           * float(request.POST['material'])/1000000, 2)
        else:
            result = ''

        cal = WorkCalendar()
        html_calendar = cal.formatmonth(self.year, self.month, withyear=True)
        html_calendar = html_calendar.replace('<td ', '<td  width="150" height="150"')

        for d in self.powder_day:
            html_calendar = html_calendar.replace(f'id="{d}"', f'id="{d}" name="powder_day"')
        for d in self.optics_day:
            html_calendar = html_calendar.replace(f'id="{d}"', f'id="{d}" name="optics_day"')
        html_calendar = html_calendar.replace(f'id="{self.cyclone_day}"',
                                              f'id="{self.cyclone_day}" name="cyclone_day"')
        html_calendar = html_calendar.replace(f'id="{self.cleaning_day}"',
                                              f'id="{self.cleaning_day}" name="cleaning_day"')

        context = {'html_calendar': mark_safe(html_calendar),
                   'month': self.month,
                   'year': self.year,
                   'result': result,
                   'powders': Powder.objects.all()}

        return render(request, self.template, context)



