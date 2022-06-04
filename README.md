## Проект Yatube

Маленькая соц. сеть в которой вы можете зарегестрироваться, писать посты на различные темы, оставлять к ним комментарии, смотреть посты других пользователей в ленте, а так же подписываться на понравившихся авторов.

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/PavelZakh/hw05_final.git
```
```
cd hw05_final
```
Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
```
source env/bin/activate
```
```
python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver
```
Profit!

Требования: Python 3.8 и выше
