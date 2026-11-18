from django.contrib import admin
from .models import (
    UserProfile, Trainer, SportGroup, Student, Subject,
    Schedule, Grade, Payment
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "specialization", "phone")
    search_fields = ("last_name", "first_name", "user__username")


@admin.register(SportGroup)
class SportGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "trainer")
    list_filter = ("trainer",)
    search_fields = ("name",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "group", "phone", "user")
    list_filter = ("group",)
    search_fields = ("last_name", "first_name", "user__username")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("date", "start_time", "end_time", "group", "subject", "trainer", "status")
    list_filter = ("status", "date", "group", "trainer")
    search_fields = ("group__name", "subject__name", "trainer__last_name")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "grade", "trainer", "created_at")
    list_filter = ("grade", "subject", "trainer")
    search_fields = ("student__last_name", "student__first_name", "subject__name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "amount", "payment_date", "period", "status")
    list_filter = ("status", "payment_date")
    search_fields = ("student__last_name", "student__first_name", "period")

admin.site.site_header = "Спортивный клуб — управление"
admin.site.site_title = "Спортивный клуб"
admin.site.index_title = "Административная панель"
