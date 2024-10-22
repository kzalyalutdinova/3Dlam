from calendar import month_name

from django.shortcuts import render, redirect
from django.views import View
from .models import Order, Drawing, PrintingRegister, Day, Powder, Customer
from . import schedule_utils as sc
from django.core.exceptions import ObjectDoesNotExist
import datetime


class NewOrderView(View):
    template = 'pr_OrderCreation.html'
    today = datetime.date.today()
    context = {'today': today, 'materials': Powder.objects.all(), 'customers': Customer.objects.all()}

    def get(self, request):
        return render(request, self.template, self.context)

    def post(self, request):

        if 'back' in request.POST:
            return redirect(f'/mycalendar/printing_register')

        try:
            today = Day.objects.get(date=request.POST['datepicker'])
        except ObjectDoesNotExist:
            pass

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
                register = PrintingRegister.objects.create(order=order,
                                                           month=sc.months_list[int(
                                                               request.POST['datepicker'].split('-')[1]) - 1],
                                                           year=int(request.POST['datepicker'].split('-')[0])
                                                           )

            if 'ready' in request.POST:
                order.ready = True
                order.save()

            for file in request.FILES.getlist('drawings'):
                Drawing.objects.create(file=file, order=order)

        return render(request, self.template, self.context)
