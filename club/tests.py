import os
from unittest import mock

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import Grade, Payment, Schedule, Student, Trainer

DEMO_ENV = {"DEMO_PASSWORD": "test-pass-123"}

# В тестах: обычное хранилище статики (без собранного manifest) и быстрый хеш паролей.
FAST_TEST_SETTINGS = override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)


@FAST_TEST_SETTINGS
class SeedDemoTests(TestCase):
    def seed(self):
        with mock.patch.dict(os.environ, DEMO_ENV):
            call_command("seed_demo", stdout=open(os.devnull, "w"))

    def test_fills_every_table(self):
        self.seed()
        self.assertEqual(Trainer.objects.count(), 3)
        self.assertEqual(Student.objects.count(), 12)
        self.assertGreater(Schedule.objects.filter(status="published").count(), 0)
        self.assertTrue(Schedule.objects.filter(status="cancelled").exists())
        self.assertEqual(Grade.objects.count(), 36)
        self.assertEqual(Payment.objects.count(), 24)

    def test_second_run_does_not_duplicate(self):
        self.seed()
        self.seed()
        self.assertEqual(User.objects.count(), 16)  # admin + 3 тренера + 12 учеников

    def test_requires_password_env(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(Exception):
                call_command("seed_demo", stdout=open(os.devnull, "w"))
        self.assertFalse(User.objects.exists())


@FAST_TEST_SETTINGS
class PagesTests(TestCase):
    def setUp(self):
        with mock.patch.dict(os.environ, DEMO_ENV):
            call_command("seed_demo", stdout=open(os.devnull, "w"))

    def test_public_pages_open(self):
        for url in ["/", "/schedule/", "/login/", "/register/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_each_role_sees_own_dashboard(self):
        cases = [
            ("student1", "/student/", "Нурланов"),
            ("trainer1", "/trainer/", "Сагинтаев"),
            ("admin", "/club-admin/", ""),
        ]
        for username, url, text in cases:
            self.client.login(username=username, password=DEMO_ENV["DEMO_PASSWORD"])
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, username)
            self.assertContains(response, text)
            self.client.logout()

    def test_student_sees_only_own_grades(self):
        self.client.login(username="student1", password=DEMO_ENV["DEMO_PASSWORD"])
        response = self.client.get("/student/grades/")
        own = Student.objects.get(user__username="student1")
        other = Student.objects.get(user__username="student2")
        self.assertEqual(list(response.context["grades"]), list(own.grades.all()))
        self.assertFalse(set(response.context["grades"]) & set(other.grades.all()))


class ProductionSettingsTests(TestCase):
    """Запуск в боевом режиме без секретного ключа должен падать, а не стартовать с ключом по умолчанию."""

    def run_check(self, extra_env):
        import subprocess
        import sys
        from django.conf import settings

        env = {k: v for k, v in os.environ.items() if k not in ("DJANGO_DEBUG", "DJANGO_SECRET_KEY")}
        env.update(extra_env)
        return subprocess.run(
            [sys.executable, "manage.py", "check"],
            cwd=settings.BASE_DIR, env=env, capture_output=True, text=True,
        )

    def test_refuses_to_start_without_secret_key(self):
        result = self.run_check({})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY", result.stderr)

    def test_starts_with_secret_key(self):
        result = self.run_check({"DJANGO_SECRET_KEY": "x" * 50})
        self.assertEqual(result.returncode, 0, result.stderr)
