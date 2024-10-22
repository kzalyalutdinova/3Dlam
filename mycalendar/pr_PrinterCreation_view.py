from calendar import month_name

from django.shortcuts import render, redirect
from django.views import View
from .models import Printer, PrinterModels


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
