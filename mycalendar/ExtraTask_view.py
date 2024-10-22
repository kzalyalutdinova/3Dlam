from django.shortcuts import render, redirect
from django.views import View
from .models import Day, ExtraTask
from django.core.exceptions import ObjectDoesNotExist



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