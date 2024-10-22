from decimal import Decimal
from django.shortcuts import render, redirect
from django.views import View
from .models import Material, Day, Powder
from django.core.exceptions import ObjectDoesNotExist, ValidationError
import datetime
from . import schedule_utils as sc


def if_thursday(day, day_check=3):
    if day.weekday() == day_check:
        return True, day
    elif day.weekday() < day_check:
        diff = 7- day_check + day.weekday()
        last_thursday = day - datetime.timedelta(days=diff)
        return False, last_thursday
    elif day.weekday() > day_check:
        diff = day.weekday() - day_check
        # next_thursday = day + datetime.timedelta(days=diff)
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