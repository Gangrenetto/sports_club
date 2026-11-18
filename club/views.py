from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render

from .forms import GradeForm, PaymentForm, RegisterForm, ScheduleForm
from .models import Grade, Payment, Schedule, Student, Trainer, UserProfile


def ensure_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def home(request):
    today = date.today()
    schedule = (
        Schedule.objects
        .filter(status="published", date__gte=today)
        .select_related("group", "subject", "trainer")[:12]
    )
    return render(request, "club/home.html", {"schedule": schedule})


def public_schedule(request):
    schedule = (
        Schedule.objects
        .filter(status="published")
        .select_related("group", "subject", "trainer")
        .order_by("date", "start_time")
    )
    return render(request, "club/schedule.html", {"schedule": schedule})


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, role="student")
            Student.objects.create(
                user=user,
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
            )
            login(request, user)
            messages.success(request, "Регистрация выполнена.")
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "club/register.html", {"form": form})


@login_required
def dashboard(request):
    profile = ensure_profile(request.user)

    if profile.role == "admin" or request.user.is_superuser:
        return redirect("admin_dashboard")
    if profile.role == "trainer":
        return redirect("trainer_dashboard")
    return redirect("student_dashboard")


@login_required
def student_dashboard(request):
    profile = ensure_profile(request.user)
    if profile.role != "student":
        return redirect("dashboard")

    student = get_object_or_404(Student, user=request.user)
    grades = student.grades.select_related("subject")[:5]
    payments = student.payments.all()[:5]
    average = student.grades.aggregate(avg=Avg("grade"))["avg"]

    return render(
        request,
        "club/student/dashboard.html",
        {
            "student": student,
            "grades": grades,
            "payments": payments,
            "average": average,
        },
    )


@login_required
def student_schedule(request):
    profile = ensure_profile(request.user)
    if profile.role != "student":
        return redirect("dashboard")

    student = get_object_or_404(Student, user=request.user)
    schedule = Schedule.objects.filter(
        group=student.group, status="published"
    ).select_related("group", "subject", "trainer")

    return render(
        request,
        "club/student/schedule.html",
        {"schedule": schedule, "student": student},
    )


@login_required
def student_grades(request):
    profile = ensure_profile(request.user)
    if profile.role != "student":
        return redirect("dashboard")

    student = get_object_or_404(Student, user=request.user)
    grades = student.grades.select_related("subject", "trainer")

    return render(
        request,
        "club/student/grades.html",
        {"grades": grades, "student": student},
    )


@login_required
def student_payments(request):
    profile = ensure_profile(request.user)
    if profile.role != "student":
        return redirect("dashboard")

    student = get_object_or_404(Student, user=request.user)
    payments = student.payments.all()

    return render(
        request,
        "club/student/payments.html",
        {"payments": payments, "student": student},
    )


@login_required
def trainer_dashboard(request):
    profile = ensure_profile(request.user)
    if profile.role != "trainer":
        return redirect("dashboard")

    trainer = get_object_or_404(Trainer, user=request.user)
    groups = trainer.groups.all()
    schedule = trainer.schedule.filter(status="published").select_related("group", "subject")[:10]
    grades = trainer.grades.select_related("student", "subject")[:10]

    return render(
        request,
        "club/trainer/dashboard.html",
        {"trainer": trainer, "groups": groups, "schedule": schedule, "grades": grades},
    )


@login_required
def trainer_schedule(request):
    profile = ensure_profile(request.user)
    if profile.role != "trainer":
        return redirect("dashboard")

    trainer = get_object_or_404(Trainer, user=request.user)
    schedule = trainer.schedule.select_related("group", "subject")

    return render(
        request,
        "club/trainer/schedule.html",
        {"schedule": schedule, "trainer": trainer},
    )


@login_required
def trainer_groups(request):
    profile = ensure_profile(request.user)
    if profile.role != "trainer":
        return redirect("dashboard")

    trainer = get_object_or_404(Trainer, user=request.user)
    groups = trainer.groups.prefetch_related("students")

    return render(
        request,
        "club/trainer/groups.html",
        {"groups": groups, "trainer": trainer},
    )


@login_required
def trainer_grades(request):
    profile = ensure_profile(request.user)
    if profile.role != "trainer":
        return redirect("dashboard")

    trainer = get_object_or_404(Trainer, user=request.user)
    grades = trainer.grades.select_related("student", "subject")

    return render(
        request,
        "club/trainer/grades.html",
        {"grades": grades, "trainer": trainer},
    )


@login_required
def trainer_grade_add(request):
    profile = ensure_profile(request.user)
    if profile.role != "trainer":
        return redirect("dashboard")

    trainer = get_object_or_404(Trainer, user=request.user)

    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.trainer = trainer
            grade.save()
            messages.success(request, "Оценка добавлена.")
            return redirect("trainer_grades")
    else:
        form = GradeForm(initial={"trainer": trainer})

    return render(request, "club/trainer/grade_form.html", {"form": form})


@login_required
def admin_dashboard(request):
    profile = ensure_profile(request.user)
    if profile.role != "admin" and not request.user.is_superuser:
        return redirect("dashboard")

    from .models import SportGroup, Subject

    context = {
        "students_count": Student.objects.count(),
        "trainers_count": Trainer.objects.count(),
        "groups_count": SportGroup.objects.count(),
        "subjects_count": Subject.objects.count(),
        "schedule_count": Schedule.objects.count(),
        "grades_count": Grade.objects.count(),
        "payments_count": Payment.objects.count(),
    }
    return render(request, "club/admin/dashboard.html", context)


@login_required
def admin_schedule(request):
    profile = ensure_profile(request.user)
    if profile.role != "admin" and not request.user.is_superuser:
        return redirect("dashboard")

    schedule = Schedule.objects.select_related("group", "subject", "trainer")
    return render(request, "club/admin/schedule.html", {"schedule": schedule})


@login_required
def admin_schedule_add(request):
    profile = ensure_profile(request.user)
    if profile.role != "admin" and not request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Расписание добавлено.")
            return redirect("admin_schedule")
    else:
        form = ScheduleForm()

    return render(request, "club/admin/form.html", {
        "form": form,
        "title": "Добавить расписание",
    })


@login_required
def admin_grade_add(request):
    profile = ensure_profile(request.user)
    if profile.role != "admin" and not request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Оценка добавлена.")
            return redirect("admin_dashboard")
    else:
        form = GradeForm()

    return render(request, "club/admin/form.html", {
        "form": form,
        "title": "Добавить оценку",
    })


@login_required
def admin_payment_add(request):
    profile = ensure_profile(request.user)
    if profile.role != "admin" and not request.user.is_superuser:
        return redirect("dashboard")

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Платёж добавлен.")
            return redirect("admin_dashboard")
    else:
        form = PaymentForm()

    return render(request, "club/admin/form.html", {
        "form": form,
        "title": "Добавить платёж",
    })
