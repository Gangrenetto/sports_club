# Sports Club — Django

Готовый учебный проект системы управления спортивным клубом.

## Среда
Проект рассчитан на PyCharm + Python + Django и SQLite.

## Установка в Windows

Откройте терминал PyCharm в папке проекта:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

После запуска:
- сайт: http://127.0.0.1:8000/
- расписание: http://127.0.0.1:8000/schedule/
- вход: http://127.0.0.1:8000/login/
- регистрация ученика: http://127.0.0.1:8000/register/
- Django Admin: http://127.0.0.1:8000/admin/

## Роли

### Ученик
При самостоятельной регистрации автоматически получает роль `student`.
Видит:
- своё расписание;
- свои оценки;
- свои платежи.

### Тренер
Создаётся администратором.
Видит:
- своё расписание;
- свои группы;
- учеников своих групп;
- оценки;
- может добавлять оценки.

### Администратор
Создаётся через `createsuperuser`.
Для работы кастомной панели нужно, чтобы у пользователя был `UserProfile` с ролью `admin`.
Кроме кастомной панели, администратор имеет полный Django Admin и может редактировать все таблицы.

## Основные таблицы

- UserProfile — роль пользователя.
- Student — ученики.
- Trainer — тренеры.
- SportGroup — спортивные группы.
- Subject — занятия.
- Schedule — возможное/опубликованное/отменённое расписание.
- Grade — оценки.
- Payment — платежи.

Поле `Schedule.status` позволяет хранить черновик расписания, опубликованный вариант и отменённое занятие. Для посетителей отображаются только записи со статусом `published`.

## Важно

Не добавляйте выбор роли администратора в обычную регистрацию. Это сделано специально: обычный посетитель может зарегистрироваться только как ученик.

После первого запуска рекомендуется зайти в `/admin/`, создать:
1. UserProfile;
2. Trainer;
3. SportGroup;
4. Subject;
5. Student;
6. Schedule;
7. Grade;
8. Payment.


## Демо-данные

Команда `python manage.py seed_demo` заполняет пустую базу: администратор `admin`,
тренеры `trainer1`–`trainer3`, ученики `student1`–`student12`, группы, расписание
(от сегодняшней даты), оценки и платежи. Пароль у всех демо-аккаунтов один —
из переменной окружения `DEMO_PASSWORD`. Повторный запуск ничего не дублирует.

## Локальный запуск (Linux)

```bash
uv venv .venv && uv pip install -r requirements.txt
export DJANGO_DEBUG=1 DEMO_PASSWORD=любой-пароль
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

## Выкладка на Render

Web Service, Python:

- Build Command: `bash build.sh`
- Start Command: `python manage.py migrate --noinput && python manage.py seed_demo && gunicorn sports_club.wsgi:application`
- Переменные окружения: `DJANGO_SECRET_KEY` (длинная случайная строка), `DEMO_PASSWORD`.

База — SQLite внутри сервиса. На бесплатном тарифе диск не сохраняется: после
перезапуска сайт возвращается к демо-данным, изменения посетителей пропадают.
