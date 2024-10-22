import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from .models import Order, Customer, PrintingRegister
from . import schedule_utils as sc
import copy



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
        if 'back' in request.POST:
            return redirect(f'/mycalendar/printing_register')

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