from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("schedule/", views.public_schedule, name="public_schedule"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path("student/", views.student_dashboard, name="student_dashboard"),
    path("student/schedule/", views.student_schedule, name="student_schedule"),
    path("student/grades/", views.student_grades, name="student_grades"),
    path("student/payments/", views.student_payments, name="student_payments"),

    path("trainer/", views.trainer_dashboard, name="trainer_dashboard"),
    path("trainer/schedule/", views.trainer_schedule, name="trainer_schedule"),
    path("trainer/groups/", views.trainer_groups, name="trainer_groups"),
    path("trainer/grades/", views.trainer_grades, name="trainer_grades"),
    path("trainer/grades/add/", views.trainer_grade_add, name="trainer_grade_add"),

    path("club-admin/", views.admin_dashboard, name="admin_dashboard"),
    path("club-admin/schedule/", views.admin_schedule, name="admin_schedule"),
    path("club-admin/schedule/add/", views.admin_schedule_add, name="admin_schedule_add"),
    path("club-admin/grades/add/", views.admin_grade_add, name="admin_grade_add"),
    path("club-admin/payments/add/", views.admin_payment_add, name="admin_payment_add"),
]
