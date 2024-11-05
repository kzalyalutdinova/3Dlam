from django.urls import path

from . import calendar_view

urlpatterns = [
    path("", calendar_view.CreateSchedule.as_view(), name="create_calendar"),
    path('printing_plan/new_print', calendar_view.PrintingPlanCreationView.as_view(), name='new_print'),
    path('printing_plan/ready_orders', calendar_view.ReadyOrdersView.as_view(), name='ready_orders'),
    path('printing_plan', calendar_view.PrintingPlanView.as_view(), name='pp_table'),
    path('printing_register/new_printer', calendar_view.NewPrinterView.as_view(), name='printer_creation'),
    path('printing_register/new_material', calendar_view.NewMaterialView.as_view(), name='material_creation'),
    path('printing_register/analytics', calendar_view.CustomerAnalyticsView.as_view(), name='orders_analytics'),
    path('printing_register', calendar_view.OrdersTableView.as_view(), name='orders_table'),
    path('new_order', calendar_view.NewOrderView.as_view(), name='neworder_creation'),
    path('material_table', calendar_view.MaterialTableView.as_view(), name='material_table'),
    path('<id>', calendar_view.EditSchedule.as_view(), name='edit_calendar'),
    path('<id>/extra_task',  calendar_view.ExtraTaskCreation.as_view(), name='extra_task_creation'),
]