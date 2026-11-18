from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("student", "Ученик"),
        ("trainer", "Тренер"),
        ("admin", "Администратор"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")

    def __str__(self):
        return f"{self.user.username} — {self.get_role_display()}"


class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="trainer")
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    specialization = models.CharField("Специализация", max_length=200, blank=True)
    phone = models.CharField("Телефон", max_length=30, blank=True)

    class Meta:
        verbose_name = "Тренер"
        verbose_name_plural = "Тренеры"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class SportGroup(models.Model):
    name = models.CharField("Название группы", max_length=100)
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="groups",
        verbose_name="Тренер",
    )
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Спортивная группа"
        verbose_name_plural = "Спортивные группы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student")
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    phone = models.CharField("Телефон", max_length=30, blank=True)
    date_of_birth = models.DateField("Дата рождения", null=True, blank=True)
    group = models.ForeignKey(
        SportGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name="Группа",
    )

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Subject(models.Model):
    name = models.CharField("Название занятия", max_length=150)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Занятие"
        verbose_name_plural = "Занятия"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Schedule(models.Model):
    STATUS_CHOICES = [
        ("draft", "Черновик"),
        ("published", "Опубликовано"),
        ("cancelled", "Отменено"),
    ]

    group = models.ForeignKey(
        SportGroup, on_delete=models.CASCADE, related_name="schedule", verbose_name="Группа"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="schedule", verbose_name="Занятие"
    )
    trainer = models.ForeignKey(
        Trainer, on_delete=models.SET_NULL, null=True, related_name="schedule", verbose_name="Тренер"
    )
    date = models.DateField("Дата")
    start_time = models.TimeField("Начало")
    end_time = models.TimeField("Окончание")
    room = models.CharField("Зал / место", max_length=100, blank=True)
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="draft"
    )
    comment = models.CharField("Комментарий", max_length=255, blank=True)

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписание"
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.date} {self.start_time} — {self.group} — {self.subject}"


class Grade(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="grades", verbose_name="Ученик"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="grades", verbose_name="Занятие"
    )
    trainer = models.ForeignKey(
        Trainer, on_delete=models.SET_NULL, null=True, related_name="grades", verbose_name="Тренер"
    )
    grade = models.PositiveSmallIntegerField("Оценка")
    comment = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} — {self.subject} — {self.grade}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ("paid", "Оплачено"),
        ("pending", "Ожидает оплаты"),
        ("overdue", "Просрочено"),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="payments", verbose_name="Ученик"
    )
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    payment_date = models.DateField("Дата платежа")
    period = models.CharField("Период", max_length=100)
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    comment = models.CharField("Комментарий", max_length=255, blank=True)

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self):
        return f"{self.student} — {self.amount} ₸ — {self.period}"
