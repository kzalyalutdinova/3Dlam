import datetime
from .models import User, Day, MonthYear, ToDo, JobPatternForOperators
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


months_days = {'Январь': 31,
               'Февраль': 28,
               'Март': 31,
               'Апрель': 30,
               'Май': 31,
               'Июнь': 30,
               'Июль': 31,
               'Август': 31,
               'Сентябрь': 30,
               'Октябрь': 31,
               'Ноябрь': 30,
               'Декабрь': 31}

months_list = ['Январь', 'Февраль',
               'Март', 'Апрель', 'Май',
               'Июнь', 'Июль', 'Август',
               'Сентябрь', 'Октябрь', 'Ноябрь',
               'Декабрь']

months_list_eng = ['Jan.', 'Feb.',
                   'March', 'April', 'May',
                   'June', 'July', 'Aug.',
                   'Sept.', 'Oct.', 'Nov.',
                   'Dec.']

weekdays = {'Понедельник': 'Пн',
            'Вторник': 'Вт',
            'Среда': 'Ср',
            'Четверг': 'Чт',
            'Пятница': 'Пт',
            'Суббота': 'Сб',
            'Воскресенье': 'Вс'}

weekdays_list = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']



materials_names = ['316L', 'Inconel 718', 'ЭП648 (новый)', 'Rs553 (AlMgSc)', 'Rs320 (AlSi10Cu)', 'Титановый сплав',
                   'Медный сплав БрХ', 'CoCr', 'RC-320-45', 'RC-300-45']


def leap_year_check(year):
    # Checking if the year is leap. If so, +1 day to Feb
    if year % 4 == 0:
        months_days['Февраль'] = 29
    else:
        months_days['Февраль'] = 28
    return months_days


def get_or_create_MonthYear(obj_name, shift, month_num, year):
    leap_year_check(year)
    try:
        instance = MonthYear.objects.create(name=obj_name,
                                            shift=shift,
                                            month_name=months_list[month_num - 1],
                                            year=year,
                                            days_amount=months_days[months_list[month_num - 1]],
                                            )
    except IntegrityError:
        instance = MonthYear.objects.get(name=obj_name)
    return instance


def get_or_create_day(date, weekday, month_year):
    try:
        instance = Day.objects.create(date=date, weekday=weekday, month_year=month_year, edited=False)
    except IntegrityError:
        instance = Day.objects.get(date=date)
        instance.weekday = weekday
        instance.save()
    return instance


def count_shift(month, year):
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 7 and year == 2024:
        return 0
    else:
        obj_name = f'{months_list[month - 1]}-{year}'
        previous_obj_name = f'{months_list[prev_month-1]}-{prev_year}'
        previous_obj = MonthYear.objects.get(name=previous_obj_name)
        previous_shift = previous_obj.shift
        current_shift = 4 - previous_obj.days_amount % 4

        shift = (previous_shift + current_shift) % 4
        instance = get_or_create_MonthYear(obj_name, shift, month, year)
        return instance.shift


def show_nextMonth(current_month, current_year):
    if current_month:
        next_month = (current_month + 1) % 12
        year = current_year
        if next_month == 0:
            next_month = 12
        if next_month == 1:
            year = current_year + 1
        return next_month, year


def show_prevMonth(current_month, current_year):
    if current_month:
        prev_month = current_month - 1
        year = current_year
        if prev_month <= 0:
            prev_month = 12
            year = year - 1
        return prev_month, year

tasks_list = ('Очистка оптики', 'Очистка циклона', 'Взвешивание порошка', 'Чистка установок')

def set_tasks(day_num, weekday, o_day, y_day, powder_weekday='Четверг', optics_weekday='Пятница'):
    """
    Очистка оптики (каждая пятница) -- О
    Очистка циклона (в конце месяца) -- Ц
    Взвешивание порошка (каждый четверг) -- П
    Чистка установок (в начале месяца) -- У
    -------------------------------------------
    :param day:
    :param day_num:
    :param o_day:
    :param y_day:
    :param powder_weekday:
    :param optics_weekday:
    :return:
    """

    if weekday == powder_weekday:
        return 'powder day'

    elif weekday == optics_weekday:
        return 'cleanup day'

    if day_num == o_day:
        return 'cyclone day'

    elif day_num == y_day:
        return 'cleaning day'

    return None
