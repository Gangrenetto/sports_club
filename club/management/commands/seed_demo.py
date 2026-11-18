"""Заполняет базу демонстрационными данными.

Запуск: DEMO_PASSWORD=... python manage.py seed_demo

Повторный запуск ничего не дублирует: если пользователь admin уже есть, команда выходит.
Даты занятий считаются от сегодняшнего дня, чтобы расписание всегда было «свежим».
"""
import os
from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from club.models import (
    Grade, Payment, Schedule, SportGroup, Student, Subject, Trainer, UserProfile,
)

TRAINERS = [
    # логин, имя, фамилия, специализация, телефон
    ("trainer1", "Ерлан", "Сагинтаев", "Бокс", "+7 701 100 2030"),
    ("trainer2", "Анна", "Ковалёва", "Плавание", "+7 702 200 3040"),
    ("trainer3", "Данияр", "Ахметов", "Футбол", "+7 705 300 4050"),
]

GROUPS = [
    # название, логин тренера, описание
    ("Бокс — начинающие", "trainer1", "Базовая техника, работа на мешках, ОФП. Возраст 10–14 лет."),
    ("Бокс — продвинутые", "trainer1", "Спарринги и подготовка к городским соревнованиям."),
    ("Плавание", "trainer2", "Обучение стилям кроль и брасс, бассейн 25 м."),
    ("Футбол U-14", "trainer3", "Командная тактика, техника паса, товарищеские матчи."),
]

SUBJECTS = [
    ("Техника удара", "Постановка ударов и защиты."),
    ("Спарринг", "Учебные бои в парах под контролем тренера."),
    ("Плавание кролем", "Техника дыхания и гребка."),
    ("Тактика игры", "Розыгрыш стандартов и игра в позиции."),
    ("ОФП", "Общая физическая подготовка: выносливость, сила, растяжка."),
]

STUDENTS = [
    # логин, имя, фамилия, группа, год рождения
    ("student1", "Алихан", "Нурланов", "Бокс — начинающие", 2013),
    ("student2", "Тимур", "Беков", "Бокс — начинающие", 2012),
    ("student3", "Максим", "Орлов", "Бокс — начинающие", 2013),
    ("student4", "Арман", "Касымов", "Бокс — продвинутые", 2010),
    ("student5", "Илья", "Смирнов", "Бокс — продвинутые", 2009),
    ("student6", "Айгерим", "Жумабаева", "Плавание", 2014),
    ("student7", "София", "Ким", "Плавание", 2013),
    ("student8", "Мадина", "Сейткали", "Плавание", 2012),
    ("student9", "Даниил", "Петров", "Футбол U-14", 2011),
    ("student10", "Нурсултан", "Абенов", "Футбол U-14", 2011),
    ("student11", "Руслан", "Ибраев", "Футбол U-14", 2012),
    ("student12", "Егор", "Волков", "Футбол U-14", 2011),
]

# группа, занятие, день недели (0 = понедельник), начало, конец, зал
WEEKLY = [
    ("Бокс — начинающие", "Техника удара", 0, time(16, 0), time(17, 30), "Зал единоборств"),
    ("Бокс — начинающие", "ОФП", 3, time(16, 0), time(17, 0), "Тренажёрный зал"),
    ("Бокс — продвинутые", "Спарринг", 1, time(18, 0), time(19, 30), "Зал единоборств"),
    ("Бокс — продвинутые", "Техника удара", 4, time(18, 0), time(19, 30), "Зал единоборств"),
    ("Плавание", "Плавание кролем", 0, time(9, 0), time(10, 0), "Бассейн, дорожки 1–3"),
    ("Плавание", "Плавание кролем", 2, time(9, 0), time(10, 0), "Бассейн, дорожки 1–3"),
    ("Плавание", "ОФП", 5, time(10, 0), time(11, 0), "Тренажёрный зал"),
    ("Футбол U-14", "Тактика игры", 1, time(15, 0), time(16, 30), "Стадион, поле №2"),
    ("Футбол U-14", "ОФП", 3, time(15, 0), time(16, 0), "Стадион, беговая дорожка"),
    ("Футбол U-14", "Тактика игры", 5, time(12, 0), time(13, 30), "Стадион, поле №2"),
]

GRADE_COMMENTS = {
    5: "Отличная работа, так держать.",
    4: "Хорошо, есть над чем поработать.",
    3: "Нужно подтянуть технику.",
}


class Command(BaseCommand):
    help = "Заполняет базу демонстрационными данными (только если она пустая)."

    def handle(self, *args, **options):
        if User.objects.filter(username="admin").exists():
            self.stdout.write("Демо-данные уже есть, пропускаю.")
            return

        password = os.environ.get("DEMO_PASSWORD")
        if not password:
            raise CommandError("Задайте переменную окружения DEMO_PASSWORD — пароль демо-аккаунтов.")

        with transaction.atomic():
            self._seed(password)

        self.stdout.write(self.style.SUCCESS(
            "Готово: admin, trainer1–trainer3, student1–student12 (пароль из DEMO_PASSWORD)."
        ))

    def _make_user(self, username, password, first_name="", last_name="", role="student"):
        user = User.objects.create_user(
            username=username, password=password, first_name=first_name, last_name=last_name,
        )
        UserProfile.objects.create(user=user, role=role)
        return user

    def _seed(self, password):
        today = date.today()

        admin = self._make_user("admin", password, "Администратор", "Клуба", role="admin")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        trainers = {}
        for username, first, last, spec, phone in TRAINERS:
            user = self._make_user(username, password, first, last, role="trainer")
            trainers[username] = Trainer.objects.create(
                user=user, first_name=first, last_name=last, specialization=spec, phone=phone,
            )

        groups = {}
        for name, trainer_login, description in GROUPS:
            groups[name] = SportGroup.objects.create(
                name=name, trainer=trainers[trainer_login], description=description,
            )

        subjects = {
            name: Subject.objects.create(name=name, description=description)
            for name, description in SUBJECTS
        }

        students = []
        for i, (username, first, last, group_name, year) in enumerate(STUDENTS):
            user = self._make_user(username, password, first, last, role="student")
            students.append(Student.objects.create(
                user=user,
                first_name=first,
                last_name=last,
                phone=f"+7 707 {400 + i:03d} {10 + i:02d}{20 + i:02d}",
                date_of_birth=date(year, 1 + i % 12, 1 + (i * 3) % 28),
                group=groups[group_name],
            ))

        # Расписание: прошлая неделя, текущая и две следующие.
        monday = today - timedelta(days=today.weekday())
        for week in range(-1, 3):
            for group_name, subject_name, weekday, start, end, room in WEEKLY:
                group = groups[group_name]
                lesson_date = monday + timedelta(weeks=week, days=weekday)
                status, comment = "published", ""
                if week == 2:
                    status = "draft"  # дальняя неделя ещё не утверждена
                Schedule.objects.create(
                    group=group, subject=subjects[subject_name], trainer=group.trainer,
                    date=lesson_date, start_time=start, end_time=end, room=room,
                    status=status, comment=comment,
                )
        # Одно занятие на этой неделе отменено — чтобы было видно, как выглядит статус.
        cancelled = Schedule.objects.filter(
            group=groups["Плавание"], date__gte=today, status="published",
        ).first()
        if cancelled:
            cancelled.status = "cancelled"
            cancelled.comment = "Бассейн на техническом обслуживании"
            cancelled.save()

        # Оценки: по 3 на ученика, по занятиям его группы.
        group_subjects = {}
        for group_name, subject_name, *_ in WEEKLY:
            group_subjects.setdefault(group_name, [])
            if subject_name not in group_subjects[group_name]:
                group_subjects[group_name].append(subject_name)
        for i, student in enumerate(students):
            names = group_subjects[student.group.name]
            for j in range(3):
                value = (5, 4, 5, 3, 4)[(i + j) % 5]
                Grade.objects.create(
                    student=student,
                    subject=subjects[names[j % len(names)]],
                    trainer=student.group.trainer,
                    grade=value,
                    comment=GRADE_COMMENTS[value],
                )

        # Платежи: прошлый месяц оплачен, текущий — у кого как.
        prev_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        month_names = [
            "январь", "февраль", "март", "апрель", "май", "июнь",
            "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
        ]
        for i, student in enumerate(students):
            Payment.objects.create(
                student=student, amount=Decimal("15000.00"), payment_date=prev_month.replace(day=5),
                period=f"{month_names[prev_month.month - 1]} {prev_month.year}", status="paid",
            )
            status = ("paid", "paid", "pending", "overdue")[i % 4]
            Payment.objects.create(
                student=student, amount=Decimal("15000.00"), payment_date=today.replace(day=5),
                period=f"{month_names[today.month - 1]} {today.year}", status=status,
                comment="Оплата наличными в кассе" if status == "paid" else "",
            )
