from calendar import month_name

from django.shortcuts import render, redirect
from django.views import View
from .models import Powder
from . import schedule_utils as sc
from django.core.exceptions import ObjectDoesNotExist
import datetime


class NewMaterialView(View):
    template = 'pr_MaterialCreation.html'


    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        if 'back' in request.POST:
            return redirect(f'/mycalendar/printing_register')

        if request.POST['material_name'].strip():
            try:
                powder = Powder.objects.get(name=request.POST['material_name'])
                powder.density = float(request.POST['density'])
                powder.save()
            except ObjectDoesNotExist:
                powder = Powder.objects.create(name=request.POST['material_name'],
                                               density=float(request.POST['density']))

        return render(request, self.template)
