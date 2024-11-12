import calendar
import datetime
import re
from decimal import Decimal
import json
import pytz

from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views import View
from .models import *
from . import schedule_utils as sc
from .HTML_Calendar import WorkCalendar
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.timezone import make_aware

"""
def is_master(user):
    return user.groups.filter(name='Masters').exists()
"""

"""All views in one place"""
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
        print(request.GET)
        if 'id' in request.GET:
            tasks = []
            date = Day.objects.get(date=datetime.date(year=int(request.GET['id'].split('-')[0]),
                                                      month=int(request.GET['id'].split('-')[1]),
                                                      day=int(request.GET['id'].split('-')[2])))
            for item in ToDo.objects.filter(date=date):
                task = {'name': item.task.name,'times': item.times}
                tasks.append(task)
            extra = [item.task for item in ExtraTask.objects.filter(date=date, done=True)]
            return JsonResponse({'tasks':tasks, 'extra': extra, 'date':request.GET['id']})

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


class EditSchedule(View):
    template: str = 'edit_day.html'

    context = {'date': None, 'date_name': '', 'comment': '', 'current_worker': '', 'users': []}
    users = User.objects.all()
    today = datetime.date.today()
    powder_weekday = 'Четверг'
    optics_weekday = 'Пятница'

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


def if_thursday(day, day_check=3):
    if day.weekday() == day_check:
        return True, day
    elif day.weekday() < day_check:
        diff = 7 - day_check + day.weekday()
        last_thursday = day - datetime.timedelta(days=diff)
        return False, last_thursday
    elif day.weekday() > day_check:
        diff = day.weekday() - day_check
        last_thursday = day - datetime.timedelta(days=diff)
        return False, last_thursday


def valid_dateformat(date):
    split_date = date.split(' ')
    r_month = sc.months_list_eng.index(split_date[0]) + 1
    r_date = datetime.date(int(split_date[2]), r_month, int(split_date[1].split(',')[0]))
    return r_date


class MaterialTableView(View):
    template = 'material_table.html'
    no_result_template = 'material_table_noresult.html'
    today = datetime.date.today()
    context = {}

    def get(self, request):

        flag, prev_thu = if_thursday(self.today)
        date = Day.objects.get(date=prev_thu)
        if flag and not Material.objects.filter(date=date):
            for powder in Powder.objects.all():
                Material.objects.create(name=powder,
                                        overall_weight=Decimal(0.000),
                                        closed_cans=Decimal(0.000),
                                        date=date)
        self.context['materials'] = Material.objects.filter(date=date)
        self.context['today'] = prev_thu
        return render(request, self.template, self.context)

    def post(self, request):

        if 'back-button' in request.POST:
            return redirect('/mycalendar')

        if 'datepicker' in request.POST:
            if request.POST['datepicker']:
                if request.POST['datepicker'].split(' ')[0] in sc.months_list_eng:
                    date = valid_dateformat(request.POST['datepicker'])
                else:
                    date = request.POST['datepicker']
                self.context['today'] = date
            else:
                flag, date = if_thursday(self.today)
                self.context['today'] = date

            try:
                day = Day.objects.get(date=date)
            except ValidationError:
                new_date = valid_dateformat(date)
                day = Day.objects.get(date=new_date)

            self.context['materials'] = Material.objects.filter(date=day)

            if not Material.objects.filter(date=day):
                if day.date != self.today:
                    self.context['noresult'] = 'Нет данных на этот день'
                    return render(request, self.no_result_template, self.context)
                else:
                    for powder in Powder.objects.all():
                        Material.objects.create(name=powder,
                                                overall_weight=Decimal(0.000),
                                                closed_cans=Decimal(0.000),
                                                date=day)

        if 'material-name' in request.POST:
            material_names = request.POST.getlist('material-name')

        if 'overall-weight' in request.POST:
            overall_weights = request.POST.getlist('overall-weight')

        if 'closed-cans' in request.POST:
            closed_cans = request.POST.getlist('closed-cans')

        if 'comment' in request.POST:
            comments = request.POST.getlist('comment')

        flag, _ = if_thursday(self.today)
        # flag = True
        # Editing and creating objects is available only on Thursdays

        if flag and self.context['today'] == self.today:
            date = Day.objects.get(date=self.today)
            print(date)
            for i in range(len(material_names)):
                powder = Powder.objects.get(name=material_names[i])
                try:
                    material = Material.objects.get(name=powder, date=date)
                except ObjectDoesNotExist:
                    # Creating new Material model objects
                    Material.objects.create(name=material_names[i],
                                            overall_weight=overall_weights[i],
                                            closed_cans=closed_cans[i],
                                            comment=comments[i],
                                            date=date)

                else:
                    #  Editing values in Material model objects
                    if material.overall_weight != Decimal(overall_weights[i]):
                        material.overall_weight = Decimal(overall_weights[i])
                        material.save()
                    if material.closed_cans != Decimal(closed_cans[i]):
                        material.closed_cans = Decimal(closed_cans[i])
                        material.save()
                    if material.comment != comments[i] and comments[i] != '':
                        material.comment = comments[i]
                        material.save()

        return render(request, self.template, self.context)


class ExtraTaskCreation(View):
    template = 'ExtraTaskCreation.html'
    context = {}
    def get(self, request, id):
        return render(request, self.template, self.context)

    def post(self, request, id):
        print(request.POST)
        d = day = Day.objects.get(date=id)
        if 'back' in request.POST:
            return redirect(f'/mycalendar/{id}')

        if request.POST['task'].strip():
            try:
                ExtraTask.objects.get(date=d, task=request.POST['task'])
            except ObjectDoesNotExist:
                ExtraTask.objects.create(date=d, task=request.POST['task'])
            finally:
                return redirect(f'/mycalendar/{id}')

        return render(request, self.template, self.context)


def parse_month(date: str):
    """
    :param:
    date: 'yyyy-mm-dd' (example: '2024-01-31')
    ---
    :return:
    year: int
    month_name_ru: str
    day: int
    """
    month_num = int(date.split('-')[1]) - 1
    month_name_ru = sc.months_list[month_num]
    year = int(date.split('-')[0])
    day = int(date.split('-')[2])
    return year, month_name_ru, day


class OrdersTableView(View):
    #TODO: добавить возможность удаления
    template = 'pr_OrdersTable.html'
    today = datetime.date.today()

    context = {'today': today, 'printers': Printer.objects.all(),
               'powders': Powder.objects.all(), 'customers': Customer.objects.all()}

    def get(self, request):
        self.context['powders'] = Powder.objects.all()
        self.context['printers'] = Printer.objects.all()
        register = [obj for obj in PrintingRegister.objects.filter(month=sc.months_list[self.today.month - 1],
                                                                   year=self.today.year)]
        if self.today.month - 2 < 0:
            year = self.today.year - 1
        else:
            year = self.today.year
        register.extend(PrintingRegister.objects.filter(next_month=True,
                                                        year=year,
                                                        month=sc.months_list[self.today.month - 2]))

        try:
            today = Day.objects.get(date=self.today)
        except ObjectDoesNotExist:
            pass
        else:
            self.context['days'] = [i + 1 for i in range(today.month_year.days_amount)]

        if 'value' in request.GET:
            try:
                order_id = request.GET['id'].split('&')[1]
            except IndexError:
                pass
            else:
                attr = request.GET['id'].split('&')[0]
                obj = Order.objects.get(id=order_id)
                if attr == 'material':
                    material = Powder.objects.get(name=request.GET['value'])
                    setattr(obj, attr, material)
                elif attr == 'customer':
                    try:
                        customer = Customer.objects.get(name=request.GET['value'])
                    except ObjectDoesNotExist:
                        customer = Customer.objects.create(name=request.GET['value'])
                    finally:
                        setattr(obj, attr, customer)
                else:
                    setattr(obj, attr, request.GET['value'])
                obj.save()

        orders = [obj for obj in register]
        self.context['orders'] = orders

        drawings = []
        for order in orders:
            try:
                drawing = Drawing.objects.filter(order=order.order)
            except ObjectDoesNotExist:
                drawing = []
            drawings.append(drawing)
        self.context['drawings'] = drawings
        return render(request, self.template, self.context)

    def post(self, request):
        print(request.POST)
        if 'new_order_button' in request.POST:
            return redirect('/mycalendar/new_order')

        if 'new_printer' in request.POST:
            return redirect('/mycalendar/printing_register/new_printer')

        if 'analytics' in request.POST:
            return redirect('/mycalendar/printing_register/analytics')

        if 'new_material' in request.POST:
            return redirect('/mycalendar/printing_register/new_material')

        pr_register = [obj for obj in PrintingRegister.objects.filter(month=sc.months_list[self.today.month - 1],
                                                                      year=self.today.year)]
        if self.today.month - 2 < 0:
            year = self.today.year - 1
        else:
            year = self.today.year
        pr_register.extend(PrintingRegister.objects.filter(next_month=True, year=year,
                                                           month=sc.months_list[self.today.month - 2]))

        if 'printer' in request.POST:
            order_id = request.POST['id'].split('&')[1]
            order_obj = Order.objects.get(id=order_id)
            register_obj = PrintingRegister.objects.get(order=order_obj)
            printer_id = re.search(r'[\d*]', request.POST['printer']).group(0)
            printer_obj = Printer.objects.get(sn=printer_id)
            register_obj.printer = printer_obj
            register_obj.save()

            response = {'text': printer_obj.__str__(), 'id': request.POST['id']}

            return JsonResponse(response)

        if 'search' in request.POST and request.POST['search'].strip():
            cur_month = request.POST['search'].split(' ')[0]
            i = sc.months_list.index(cur_month)
            if i - 1 < 0:
                year = int(request.POST['search'].split(' ')[1]) - 1
            else:
                year = request.POST['search'].split(' ')[1]
            pr_register = [obj for obj in PrintingRegister.objects.filter(month=cur_month, year=year)]
            pr_register.extend(PrintingRegister.objects.filter(month=sc.months_list[i-1],
                                                              year=year,
                                                              next_month=True))

        else:
            year = self.today.year
            sc.leap_year_check(year)
            cur_month = sc.months_list[self.today.month - 1]

        self.context['days'] = [i + 1 for i in range(sc.months_days[cur_month])]

        orders = [obj for obj in pr_register]
        self.context['orders'] = orders

        drawings = []
        for order in orders:
            try:
                drawing = Drawing.objects.filter(order=order.order)
            except ObjectDoesNotExist:
                drawing = []
            drawings.append(drawing)
        self.context['drawings'] = drawings

        return render(request, self.template, self.context)


class CustomerAnalyticsView(View):
    template = 'pr_OrdersAnalytics.html'
    year = datetime.date.today().year
    sc.leap_year_check(year)
    month = sc.months_list[datetime.date.today().month - 1]
    context = {'customers': [], 'totals': 0}

    def get(self, request):
        customers = Customer.objects.all()
        self.context['customers'] = []
        self.context['totals'] = 0
        for customer in customers:
            orders = Order.objects.filter(customer=customer)
            total_cost = sum([order.cost for order in orders])
            self.context['totals'] += total_cost
            orders_amount = len(orders)
            self.context['customers'].append({'name': customer.name,
                                              'orders_amount': orders_amount,
                                              'total_cost': total_cost})
        print(self.context)
        return render(request, self.template, self.context)

    def post(self, request):
        if 'filter' in request.POST:
            self.context['customers'] = []

            if request.POST['filter'] == 'all':
                customers = Customer.objects.all()
                for customer in customers:
                    orders = Order.objects.filter(customer=customer)
                    total_cost = sum([order.cost for order in orders])
                    orders_amount = len(orders)
                    self.context['customers'].append({'name': customer.name,
                                                      'orders_amount': orders_amount,
                                                      'total_cost': total_cost})
                return JsonResponse(self.context)
            elif request.POST['filter'] == 'this_year':
                customers = []
                pr = PrintingRegister.objects.filter(year=self.year)
                for order in pr:
                    if order.order.customer.name in customers:
                        for item in self.context['customers']:
                            if order.order.customer.name == item['name']:
                                item['orders_amount'] += 1
                                item['total_cost'] += order.order.cost
                                break
                    else:
                        customers.append(order.order.customer.name)
                        self.context['customers'].append({'name': order.order.customer.name,
                                                          'orders_amount': 1,
                                                          'total_cost': order.order.cost})
                return JsonResponse(self.context)
            elif request.POST['filter'] == 'period':
                if request.POST['from'].strip() != '':
                    count = 0
                    pr = []
                    customers = []
                    totals = 0
                    period_from = request.POST['from'].split('-')[0]
                    period_to = request.POST['from'].split('-')[1]
                    from_month = sc.months_list.index(period_from.split(' ')[0])
                    to_month = sc.months_list.index(period_to.split(' ')[0])
                    if int(period_from.split(' ')[1]) == int(period_to.split(' ')[1]):  # сравниваем года
                        months = sc.months_list[from_month:to_month+1]
                        for month in months:
                            pr.extend(PrintingRegister.objects.filter(year=period_from.split(' ')[1], month=month))
                    else:
                        diff_years = int(period_to.split(' ')[1]) - int(period_from.split(' ')[1]) - 1

                        months = sc.months_list[from_month:]
                        flag = len(months) - 1
                        if diff_years != 0:
                            months.extend(sc.months_list * diff_years)
                        months.extend(sc.months_list[:to_month+1])

                        for i in range(len(months)):
                            if i <= flag:
                                pr.extend(PrintingRegister.objects.filter(year=int(period_from.split(' ')[1]),
                                                                          month=months[i]))
                            elif i > flag + 12 * diff_years:
                                pr.extend(PrintingRegister.objects.filter(year=int(period_to.split(' ')[1]),
                                                                          month=months[i]))
                            else:
                                if i % (flag + 1) == 0:
                                    count += 1
                                pr.extend(PrintingRegister.objects.filter(year=int(period_from.split(' ')[1]) + count,
                                                                          month=months[i]))
                                print(months[i], int(period_from.split(' ')[1]) + count)
                    for order in pr:
                        if order.order.customer.name in customers:
                            for item in self.context['customers']:
                                if order.order.customer.name == item['name']:
                                    item['orders_amount'] += 1
                                    item['total_cost'] += order.order.cost
                                    totals += order.order.cost
                                    break
                        else:
                            customers.append(order.order.customer.name)
                            self.context['customers'].append({'name': order.order.customer.name,
                                                              'orders_amount': 1,
                                                              'total_cost': order.order.cost})
                            totals += order.order.cost
                    self.context['totals'] = totals
                    return render(request, self.template, self.context)
        return render(request, self.template, self.context)


class NewMaterialView(View):
    template = 'pr_MaterialCreation.html'
    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        if request.POST['material_name'].strip():
            try:
                powder = Powder.objects.get(name=request.POST['material_name'])
                powder.density = float(request.POST['density'])
                powder.save()
            except ObjectDoesNotExist:
                powder = Powder.objects.create(name=request.POST['material_name'],
                                               density=float(request.POST['density']))

        return render(request, self.template)


class NewOrderView(View):
    template = 'pr_OrderCreation.html'
    today = datetime.date.today()
    context = {'today': today, 'materials': Powder.objects.all(), 'customers': Customer.objects.all()}

    def get(self, request):
        print()
        regular_orders = []
        if 'pattern' in request.GET:
            item = RegularOrdersPattern.objects.get(id=int(request.GET['pattern']))
            result = {'order_name': item.name, 'customer': item.customer.name, 'amount': item.amount,
                      'material': item.material.name, 'volume': item.volume, 'cost': item.cost,
                      'datepicker': item.date, 'duration': item.duration, 'comment': item.comment}

            return JsonResponse(result)
        for item in RegularOrdersPattern.objects.all():
            try:
                images = json.loads(item.drawings)['images']
            except TypeError:
                images = None
            regular_orders.append({'item': item,
                                   'images': images
                                   })
            print(regular_orders)
        self.context['regular_orders'] = regular_orders
        return render(request, self.template, self.context)

    def post(self, request):
        # TODO: добавить шаблон постоянного заказа (все поля скопированы из заказа)
        print(request.POST)
        if request.POST['order_name'].strip() and request.POST['customer'].strip():
            try:
                customer = Customer.objects.get(name=request.POST['customer'])
            except ObjectDoesNotExist:
                customer = Customer.objects.create(name=request.POST['customer'])
            finally:
                order = Order.objects.create(name=request.POST['order_name'],
                                             customer=customer,
                                             amount=request.POST['amount'],
                                             material=Powder.objects.get(name=request.POST['material']),
                                             volume=request.POST['volume'],
                                             cost=request.POST['cost'],
                                             comment=request.POST['comment'],
                                             date=request.POST['datepicker'],
                                             duration=request.POST['duration'])
            try:
                register = PrintingRegister.objects.get(order=order)
            except ObjectDoesNotExist:
                date = datetime.datetime.strptime(request.POST['datepicker'], '%Y-%m-%d').date()
                end_date = date + datetime.timedelta(days=int(request.POST['duration']))
                if end_date.month != date.month:
                    next_month = True
                else:
                    next_month = False

                register = PrintingRegister.objects.create(order=order,
                                                           next_month=next_month,
                                                           month=sc.months_list[int(
                                                               request.POST['datepicker'].split('-')[1]) - 1],
                                                           year=int(request.POST['datepicker'].split('-')[0])
                                                           )

            drawings = []
            for file in request.FILES.getlist('drawings'):
                drawing = Drawing.objects.create(file=file, order=order)
                drawings.append(drawing)

            if 'ready' in request.POST:
                order.ready = True
                order.save()

            if 'regular' in request.POST:
                order.regular = True
                order.save()
                try:
                    regular_order = RegularOrdersPattern.objects.get(
                        name=request.POST['order_name'],
                        customer=customer,
                        material=Powder.objects.get(name=request.POST['material']),
                        volume=request.POST['volume'])
                except ObjectDoesNotExist:
                    regular_order = RegularOrdersPattern.objects.create(
                        name=request.POST['order_name'],
                        customer=customer,
                        amount=request.POST['amount'],
                        material=Powder.objects.get(name=request.POST['material']),
                        volume=request.POST['volume'],
                        cost=request.POST['cost'],
                        comment=request.POST['comment'],
                        date=request.POST['datepicker'],
                        duration=request.POST['duration'],
                        drawings=json.dumps({'images': [str(img.file) for img in drawings]},
                                            ensure_ascii=False)
                    )
                else:
                    if not drawings:
                        images = json.loads(regular_order.drawings)
                        for image in images['images']:
                            Drawing.objects.create(file=image, order=order)
        if 'submit_button' in request.POST:
            return redirect('/mycalendar/printing_register')
        return render(request, self.template, self.context)


class NewPrinterView(View):
    template = 'pr_PrinterCreation.html'
    context = {}

    def get(self, request):
        self.context['models'] = PrinterModels.objects.all()
        return render(request, self.template, self.context)

    def post(self, request):
        self.context['models'] = PrinterModels.objects.all()

        if 'back' in request.POST:
            return redirect(f'/mycalendar/printing_register')

        if request.POST['model_name'].strip():
            model = PrinterModels.objects.get(name=request.POST['model_name'])
            Printer.objects.create(model=model)

        return render(request, self.template, self.context)

class PrintingPlanCreationView(View):
    template = 'pp_PrintingPlanCreation.html'
    context = {'items': []}

    def get(self, request):
        self.context['printers'] = Printer.objects.all()
        self.context['powders'] = Powder.objects.all()
        self.context['standard_operations'] = PPStandardOperations.objects.all()
        return render(request, self.template, self.context)

    def post(self, request):
        print(request.POST)
        self.context['printers'] = Printer.objects.all()
        self.context['powders'] = Powder.objects.all()
        self.context['standard_operations'] = PPStandardOperations.objects.all()

        if 'submit_button' in request.POST:
            pp = PrintingPlan.objects.create(file_num=int(request.POST['file_num']),
                                             printer=Printer.objects.get(sn=int(request.POST['printer'])),
                                             priority=request.POST['priority'])

            if request.POST['comment'].strip():
                pp.comments = request.POST['comment']
                pp.save()

            if 'drawing' in request.FILES:
                PPDrawing.objects.create(pp=pp, file=request.FILES['drawing'])

            if 'operations' in request.POST:
                pp.operations = json.dumps({'operations':
                                                [op for op in request.POST.getlist('operations') if op and op.strip()]},
                                           ensure_ascii=False)
                pp.save()
            if 'orders' in request.POST:
                orders_id = request.POST.getlist('orders')
                for order_id in orders_id:
                    order = Order.objects.get(id=int(order_id))
                    print(order.name)
                    pp.orders.add(order)
                    pp.save()
            return redirect(f'/mycalendar/printing_plan')
        elif 'powder' in request.POST:
            orders = []
            dates = []      # [(месяц (по-русски), год), ...]
            month = int(request.POST['month'])
            # Фильтруем заказы по дате и материалу
            if month - 3 >= 0:
                for i in sc.months_list[month - 2:month + 1]:
                    dates.append((i, int(request.POST['year'])))
            else:
                for i in sc.months_list[13 + (month - 3):]:
                    dates.append((i, int(request.POST['year']) - 1))
                for i in sc.months_list[:month + 1]:
                    dates.append((i, int(request.POST['year'])))

            for item in Order.objects.filter(material=Powder.objects.get(name=request.POST['powder'])):
                pr = PrintingRegister.objects.get(order=item)
                if item.regular or ((pr.month, pr.year) in dates):
                    images = [str(img.file) for img in Drawing.objects.filter(order=item)]
                    order = {'name': item.name, 'images': images, 'customer': item.customer.name, 'id': item.id}
                    orders.append(order)
            return JsonResponse({'orders': orders})

        return render(request, self.template, self.context)


class PrintingPlanView(View):
    template = 'pp_PrintingPlanTable.html'
    context = {'items': [], 'current_printer': None, 'printers': []}

    def get(self, request):
        print(request.GET)
        print(request.user)
        print(request.user.is_superuser)
        self.context['printers'] = []
        #
        if request.user.is_superuser:
            self.context['printers'] = ['Готовые заказы']
            self.context['printers'].extend(Printer.objects.all())
        else:
            try:
                ReadyOrder.objects.filter(ready=False)
            except ObjectDoesNotExist:
                pass
            else:
                self.context['printers'] = ['Готовые заказы']
            finally:
                for printer in Printer.objects.all():
                    if PrintingPlan.objects.filter(printer=printer, ready=False).exists():
                        self.context['printers'].append(printer)
        try:
            self.context['current_printer'] = self.context['printers'][1]
        except IndexError:
            self.context['current_printer'] = Printer.objects.all()[0]
        self.context['items'] = []

        if 'search_button' in request.GET:
            if request.GET['printer'] == 'Готовые заказы':
                return redirect(f'/mycalendar/printing_plan/ready_orders')
            sn = re.findall(r'\((.*?)\)', request.GET['printer'])[0]
            self.context['current_printer'] = Printer.objects.get(sn=sn)

        for item in PrintingPlan.objects.filter(printer=self.context['current_printer']):
            try:
                drawing = PPDrawing.objects.get(pp=item).file
            except ObjectDoesNotExist:
                drawing = None
            try:
                material = item.orders.all().first().material.name
            except AttributeError or IndexError:
                material = 'Не был привязан заказ'
            self.context['items'].append({'item': item,
                                          'material': material,
                                          'drawing':drawing,
                                          'operations': json.loads(item.operations)['operations']})

        return render(request, self.template, self.context)

    def post(self, request):
        print(request.POST)
        if 'id' in request.POST:
            item = PrintingPlan.objects.get(id=int(request.POST['id']))
            if 'ready' not in request.POST and 'delete' not in request.POST:
                attr = request.POST['attr']
                if attr == 'file_num':
                    value = int(request.POST['value'])
                elif attr == 'operations':
                    operations = request.POST.getlist('value[]')
                    operations.extend(json.loads(item.operations)['operations'])
                    value = json.dumps({'operations': operations}, ensure_ascii=False)
                elif attr == 'comments':
                    value = request.POST['value']
                else:
                    value = json.loads(request.POST['value'])
                setattr(item, attr, value)
                item.save()
            elif 'ready' in request.POST:
                if request.POST['ready'] == 'True':
                    item.ready = True
                    item.datetime_end = pytz.timezone('Europe/Moscow').localize(
                        datetime.datetime.strptime(request.POST['datetime_end'], '%d.%m.%Y, %H:%M:%S'))
                    # Перемещаем напечатанный заказ в модель "Готовые заказы"
                    for order in item.orders.all():
                        ReadyOrder.objects.create(order=order)
                else:
                    item.ready = False
                    item.datetime_end = None
                item.save()
            else:
                item.delete()
        elif 'new_pp' in request.POST:
            return redirect(f'/mycalendar/printing_plan/new_print')
        elif 'new_material' in request.POST:
            return redirect('/mycalendar/printing_register/new_material')
        elif 'new_printer' in request.POST:
            return redirect('/mycalendar/printing_register/new_printer')

        return render(request, self.template, self.context)


class ReadyOrdersView(View):
    template = 'pp_ReadyOrdersTable.html'
    context = {}

    def get(self, request):
        print(request.GET)
        self.context['items'] = []
        for item in ReadyOrder.objects.all():
            item = {'item': item,
                    'drawing': [dr.file for dr in Drawing.objects.filter(order=item.order)]}
            print(item['drawing'])
            self.context['items'].append(item)
        return render(request, self.template, self.context)

    def post(self, request):
        print(request.POST)
        item = ReadyOrder.objects.get(id=int(request.POST['id']))
        if 'delete' in request.POST:
            item.delete()
        else:
            attr = request.POST['attr']
            if attr == 'amount':
                value = int(request.POST['value'])
            elif attr == 'comments':
                if request.POST['value'].strip():
                    value = request.POST['value']
                else:
                    value = None
            else:
                # attr = 'hidden' or 'ready'
                if request.POST['value'].lower() == 'true':
                    value = True
                else:
                    value = False
            setattr(item, attr, value)
            item.save()

        return render(request, self.template, self.context)