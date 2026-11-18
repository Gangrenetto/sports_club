# Sports Club — Visual Studio Code

Готовый Django-проект для Visual Studio Code и Windows.

## 1\. Открытие проекта

Распакуйте архив и в VS Code выберите:

**File → Open Folder → sports\_club**

После открытия VS Code должен видеть папку `.vscode`.

## 2\. Создание виртуального окружения

Откройте:

**Terminal → New Terminal**

В PowerShell выполните:

```powershell
python -m venv .venv
```

Затем:

```powershell
.venv\\\\\\\\\\\\\\\\Scripts\\\\\\\\\\\\\\\\Activate.ps1
```

Если PowerShell запрещает запуск скрипта, можно использовать:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

и снова:

```powershell
.venv\\\\\\\\\\\\\\\\Scripts\\\\\\\\\\\\\\\\Activate.ps1
```

## 3\. Установка Django

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4\. Создание базы данных

```powershell
python manage.py makemigrations
python manage.py migrate
```

## 5\. Создание администратора

```powershell
python manage.py createsuperuser
```

Заполните имя пользователя, email и пароль.

## 6\. Запуск

```powershell
python manage.py runserver
```

Откройте:

http://127.0.0.1:8000/

## 7\. Запуск через VS Code

В проекте уже есть `.vscode/launch.json`.

Нажмите:

**Run and Debug → Django: runserver → Start**

VS Code запустит Django с отладчиком.

## Страницы

Главная:
http://127.0.0.1:8000/

Расписание:
http://127.0.0.1:8000/schedule/

Регистрация:
http://127.0.0.1:8000/register/

Вход:
http://127.0.0.1:8000/login/

Личный кабинет:
http://127.0.0.1:8000/dashboard/

Django Admin:
http://127.0.0.1:8000/admin/

## Роли

Ученик:

* своё расписание;
* свои оценки;
* свои платежи.

Тренер:

* своё расписание;
* свои группы;
* ученики своих групп;
* оценки;
* добавление оценок.

Администратор:

* полное управление через Django Admin;
* управление расписанием;
* управление оценками;
* управление платежами.

## Важный порядок заполнения

После создания суперпользователя:

1. Откройте `/admin/`.
2. Создайте пользователей.
3. Создайте `UserProfile` и назначьте роли.
4. Создайте тренеров.
5. Создайте спортивные группы.
6. Создайте занятия.
7. Создайте учеников.
8. Назначьте учеников в группы.
9. Создайте расписание.
10. Поставьте расписанию статус `Опубликовано`.

Обычная регистрация на сайте создаёт только ученика.

Не выдавайте роль администратора через обычную регистрацию.

