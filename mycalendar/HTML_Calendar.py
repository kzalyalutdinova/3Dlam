from calendar import HTMLCalendar
from .models import User, Day, MonthYear
from . import schedule_utils as sc


class WorkCalendar(HTMLCalendar):
    def __init__(self, users=None):
        super(WorkCalendar, self).__init__()
        self.users = users

    def formatday(self, day, weekday, month_days):
        """
            Return a day as a table cell.
        """

        users_from_day = []
        if day != 0:
            date_name = str(Day.objects.get(date=month_days[day - 1].date).date)

            users_from_day = Day.objects.get(date=month_days[day - 1].date)
            users_from_day = users_from_day.user.all()
        users_html = "<ul>"
        for user in users_from_day:
            users_html += user.name + "<br>"
        users_html += "</ul>"

        if day == 0:
            s = '<td class="noday" id="noday">&nbsp;</td>'  # day outside month
        else:
            s = (f'<td class="{self.cssclasses[weekday]}" ' + ''
                 f'id="{date_name}" '
                 f'onclick=EditDay("{date_name}")>'
                 f'{day}{users_html}</td>')
        return s

    def formatweek(self, theweek, month_days):
        """
            Return a complete week as a table row.
        """

        s = ''.join(self.formatday(d, wd, month_days) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        """
            Return a formatted month as a table.
        """
        ru_month = sc.months_list[themonth - 1]
        month_year_obj = MonthYear.objects.get(name=f'{ru_month}-{theyear}')
        month_days = Day.objects.filter(month_year=month_year_obj)
        first_day = '2024-08-01'
        # date = '2024-08-01'
        users = []
        v = []
        a = v.append
        a('<table border="1" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, month_days))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)
