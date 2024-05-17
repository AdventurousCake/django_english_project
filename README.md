# Project English Fixer

>⭐ Открыть проект >>> https://engproj9.servehttp.com/

[//]: # (### Открыть проект: link)

Проект English Fixer позволяет исправить ошибки в предложениях на английском, перефразирование предложений используя API reverso.net.
Также предоставляет всю необходимую информацию на одной странице.
Можно делиться ссылкой на исправленный текст.

### Возможности:
- Исправление ошибок в предложении
- Перефразирование предложений
- Функция перевода
- Сохранение ссылки на фикс + Share link
- Профиль пользователя
- Статистика пользователя
- Статистика запросов
- Мини quiz
- Регистрация и авторизация пользователей + Github Auth
- Unit тесты
- Docker

### Как запустить
- Создать .env файл
- chmod +x ./entrypoint.sh 
- docker-compose up -d --build
- docker-compose exec web python manage.py migrate --noinput
- docker-compose exec web python manage.py collectstatic --no-input --clear 
- docker-compose exec web python manage.py createsuperuser

---
### Screenshots
### Main page
![img](readme_imgs/1.png)
### Result page
![img](readme_imgs/2.png)
### List page
![img](readme_imgs/3.png)
### Profile page
![img](readme_imgs/4.png)