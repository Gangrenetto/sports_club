from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Grade, Payment, Schedule, Student


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Имя", max_length=100)
    last_name = forms.CharField(label="Фамилия", max_length=100)
    email = forms.EmailField(label="Email", required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = (
            "group", "subject", "trainer", "date",
            "start_time", "end_time", "room", "status", "comment"
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "comment": forms.TextInput(attrs={"class": "form-control"}),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ("student", "subject", "trainer", "grade", "comment")
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("student", "amount", "payment_date", "period", "status", "comment")
        widgets = {
            "payment_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ("first_name", "last_name", "phone", "date_of_birth", "group")
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }
