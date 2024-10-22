import re
from django.shortcuts import render, redirect
from django.views import View
from .models import Order, Drawing, PrintingRegister, Day, Printer, Powder, Customer
from . import schedule_utils as sc
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.http import JsonResponse


def parse_month(date:str):
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
    template = 'pr_OrdersTable.html'
    today = datetime.date.today()

    context = {'today': today, 'printers': Printer.objects.all(),
               'powders': Powder.objects.all(), 'customers': Customer.objects.all()}

    def get(self, request):
        self.context['powders'] = Powder.objects.all()
        self.context['printers'] = Printer.objects.all()
        register = PrintingRegister.objects.filter(month=sc.months_list[self.today.month - 1], year=self.today.year)
        
        try:
            today = Day.objects.get(date=self.today)
        except ObjectDoesNotExist:
            pass
        else:
            self.context['days'] = [i+1 for i in range(today.month_year.days_amount)]

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


        pr_register = PrintingRegister.objects.filter(month=sc.months_list[self.today.month - 1],
                                                   year=self.today.year)

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
            year = request.POST['search'].split(' ')[1]
            pr_register = PrintingRegister.objects.filter(month=cur_month, year=year)
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