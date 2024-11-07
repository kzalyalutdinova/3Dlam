from django.contrib import admin
from .models import *


# Register your models here.
class UserLevelAdmin(admin.ModelAdmin):
    list_display = ('date', 'weekday', 'user', 'comment')


admin.site.register(User)
admin.site.register(Day)
admin.site.register(MonthYear)
admin.site.register(ToDo)
admin.site.register(Material)
admin.site.register(Order)
admin.site.register(Printer)
admin.site.register(PrintingRegister)
admin.site.register(Drawing)
admin.site.register(Powder)
admin.site.register(Customer)
admin.site.register(PrinterModels)
admin.site.register(JobPatternForOperators)
admin.site.register(ExtraTask)
admin.site.register(PrintingPlan)
admin.site.register(PPDrawing)
admin.site.register(PPStandardOperations)
admin.site.register(ReadyOrder)

