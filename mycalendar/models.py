from django.db import models
from django.utils.translation import gettext as _


# Create your models here.
class User(models.Model):
    name = models.CharField(_("Worker's name"), max_length=100)
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['id']


class MonthYear(models.Model):
    name = models.CharField(_('Name'), max_length=50, unique=True)
    month_name = models.CharField(_('Month'), max_length=50, blank=True)
    year = models.PositiveIntegerField(_('Year'), blank=False, default=0)
    days_amount = models.PositiveSmallIntegerField(_('Amount of days'), blank=False, default=31)
    shift = models.SmallIntegerField(_('Shift'), blank=False, default=0)

    def __str__(self):
        return f'{self.name}'


class Day(models.Model):
    date = models.DateField(_('Date'), editable=False,  unique=True)
    weekday = models.CharField(_('Weekday'), max_length=12, null=True)
    user = models.ManyToManyField(User)
    month_year = models.ForeignKey(MonthYear, on_delete=models.SET_NULL, null=True)
    comment = models.TextField(_('Comment'), blank=True)
    edited = models.BooleanField(_('Day has been edited'), blank=False, default=False)

    def __str__(self):
        return f'{self.date}, {self.weekday}'


class JobPatternForOperators(models.Model):
    name = models.CharField(_('Job pattern'), unique=True, max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Job Patterns For Operators"


class ToDo(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(JobPatternForOperators, on_delete=models.SET_NULL, null=True)
    date = models.ForeignKey(Day, on_delete=models.SET_NULL, null=True)
    times = models.PositiveSmallIntegerField(_('Number of times the task has been done'), default=0, blank=False)

    def __str__(self):
        return f'{self.id}: {self.date} - {self.task}'

    class Meta:
        ordering = ['id']

class ExtraTask(models.Model):
    task = models.CharField(_('Task'), max_length=200)
    date = models.ForeignKey(Day, on_delete=models.SET_NULL, null=True)
    done = models.BooleanField(_('Is the task done?'), default=False)

    def __str__(self):
        return f'{self.date} - {self.task}'


class Powder(models.Model):
    name = models.CharField(_('Material name'), max_length=20, unique=True)
    density = models.DecimalField(_('Density of the material'), max_digits=5, decimal_places=2)

    def __str__(self):
        return f'{self.name}'

class Material(models.Model):

    name = models.ForeignKey(Powder, on_delete=models.SET_NULL, null=True)
    overall_weight = models.DecimalField(_('Net weight overall'), max_digits=7, decimal_places=3)
    closed_cans = models.DecimalField(_('Powder amount in closed cans'), max_digits=7, decimal_places=3)
    comment = models.CharField(_('Comment'), max_length=300, blank=True)
    date = models.ForeignKey(Day, on_delete=models.SET_NULL, null=True, limit_choices_to={'weekday': 'Четверг'})

    def __str__(self):
        return f'{self.date} - {self.name}'

    class Meta:
        ordering = ['-date', 'name']

class Customer(models.Model):
    name = models.CharField(_("Customer's name"), max_length=200, unique=True)

    def __str__(self):
        return f'{self.name}'


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('The name of the order'), max_length=200)
    amount = models.PositiveSmallIntegerField(_('Amount of details to produce'), default=1)
    material = models.ForeignKey(Powder, on_delete=models.SET_NULL, null=True)
    volume = models.DecimalField(_('Volume of the model2'), max_digits=5, decimal_places=2, default=0)
    cost = models.PositiveIntegerField(_('Order cost'))
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    ready = models.BooleanField(_('Is the order ready?'), default=False)
    comment = models.CharField(_('Comment'), max_length=300, blank=True)
    date = models.CharField(_('Date of the order'), max_length=30)
    duration = models.PositiveSmallIntegerField(_('Order completion time'), default=1)
    regular = models.BooleanField(_('Is the order regular?'), default=False)

    def __str__(self):
        return f'{self.name}-{self.date}'


class PrinterModels(models.Model):
    CHOICES_MODEL = (('Mini', 'Mini'), ('Mid', 'Mid'), ('Maxi', 'Maxi'), ('Общее', 'Общее'))
    name = models.CharField(max_length=50, choices=CHOICES_MODEL)

    def __str__(self):
        return self.name

class Printer(models.Model):
    sn = models.AutoField(primary_key=True)
    model = models.ForeignKey(PrinterModels, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.model} ({self.sn})'


class PrintingRegister(models.Model):
    month = models.CharField(_('Month'), max_length=20, default=0)
    year = models.PositiveSmallIntegerField(_('Year'), default=2024)
    next_month = models.BooleanField(_('Will the order be completed next month?'), default=False)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    printer = models.ForeignKey(Printer, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.order}'

class Drawing(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    file = models.ImageField(_('Drawing for detail ordered'), upload_to=f"uploads/", max_length=1000)

    def __str__(self):
        return f'{self.order}'


class PrintingPlan(models.Model):
    CHOICES_PRIORITY = (('1', '1-й приоритет'), ('2', '2-й приоритет'), ('3', '3-й приоритет'), ('0', 'Термичка'))

    id = models.AutoField(primary_key=True)
    file_num = models.PositiveSmallIntegerField(_('File №'), null=True)
    orders = models.ManyToManyField(Order, blank=True)
    # material = models.ForeignKey(Powder, on_delete=models.SET_NULL, null=True)
    printer = models.ForeignKey(Printer, on_delete=models.SET_NULL, null=True)
    operations = models.JSONField(_('Operations'), blank=True, null=True)
    comments = models.CharField(_('Comments on printing'), max_length=200, blank=True)
    ready = models.BooleanField(_('Is it ready?'), default=False, blank=False)
    datetime_end = models.DateTimeField(_('End date and time of the printing'), blank=True, null=True)
    priority = models.CharField(_('Priority'), max_length=1, choices=CHOICES_PRIORITY)
    hidden = models.BooleanField(_('Is it hidden in the table'), default=False, blank=False)

    class Meta:
        verbose_name = "Printing Plan"
        verbose_name_plural = "Printing Plan"
        ordering = ['id']


class PPDrawing(models.Model):
    id = models.AutoField(primary_key=True)
    pp = models.ForeignKey(PrintingPlan, on_delete=models.SET_NULL, null=True)
    file = models.ImageField(_('Drawing for printing plan'), upload_to=f"printing_plan/", max_length=1000)

    def __str__(self):
        return f'{self.pp}'

    class Meta:
        verbose_name = "Drawing for Printing Plan"
        verbose_name_plural = "Drawings for Printing Plan"


class PPStandardOperations(models.Model):
    name = models.CharField(_('Name'), max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Standard Operation for Printing Plan"
        verbose_name_plural = "Standard Operations for Printing Plan"


class ReadyOrder(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveSmallIntegerField(_('Amount of details'), default=0)
    comments = models.CharField(_('Comments on packing'), max_length=200, blank=True)
    ready = models.BooleanField(_('Is it ready?'), default=False, blank=False)
    hidden = models.BooleanField(_('Is it hidden in the table'), default=False, blank=False)

    class Meta:
        verbose_name = "Ready order"
        verbose_name_plural = "Ready orders"

class RegularOrdersPattern(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(_('The name of the order'), max_length=200)
    amount = models.PositiveSmallIntegerField(_('Amount of details to produce'), default=1)
    material = models.ForeignKey(Powder, on_delete=models.SET_NULL, null=True)
    volume = models.DecimalField(_('Volume of the model2'), max_digits=5, decimal_places=2, default=0)
    cost = models.PositiveIntegerField(_('Order cost'))
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    ready = models.BooleanField(_('Is the order ready?'), default=False)
    comment = models.CharField(_('Comment'), max_length=300, blank=True)
    date = models.CharField(_('Date of the order'), max_length=30)
    duration = models.PositiveSmallIntegerField(_('Order completion time'), default=1)
    regular = models.BooleanField(_('Is the order regular?'), default=True)
    drawings = models.JSONField(_('Drawings Paths'), blank=True, null=True)

    def __str__(self):
        return f'{self.name}-{self.date}'

    class Meta:
        verbose_name = "Regular Orders Pattern"
        verbose_name_plural = "Regular Orders Patterns"
