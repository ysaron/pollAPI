# pollAPI

## Установка (локально, Linux)

Клонировать репозиторий
```shell
git clone https://github.com/ysaron/pollAPI.git
cd pollAPI
```

Создать и активировать виртуальное окружение
```shell
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости
```shell
pip3 install -r requirements.txt
```

Создать файл `.env` и задать в нем переменную `TOKEN`.

Создать и применить миграции
```shell
cd pollAPI
python3 manage.py makemigrations
python3 manage.py migrate
```

Создать суперпользователя
```shell
python3 manage.py createsuperuser
```

Запуск
```shell
python3 manage.py runserver
```

## Администрирование
Админ-панель: http://127.0.0.1:8000/admin/

### Создание опросов

1. Создание экземпляра Poll. Флаг Ready следует устанавливать после создания всех вопросов в опросе - до тех пор опрос не будет доступен через API.
2. Создание экземпляров Question вместе со связанными Option (в случае типа вопроса "Ответ текстом" создание вариантов не имеет эффекта). 

## Использование

Базовый URL: http://127.0.0.1:8000/api/v1/  
Поскольку browsable API в DRF без дополнительных библиотек не поддерживает отправку HTTP заголовков, в примерах используется cURL.

### Аутентификация

Создание пользователя
```shell
curl -X POST http://127.0.0.1:8000/auth/users/ --data "username=user01&password=password123"
```

Получение токена
```shell
curl -X POST http://127.0.0.1:8000/auth/token/login/ --data "username=user01&password=password123"
```

### Эндпойнты

- **GET /active_polls/**  
  Получение списка активных опросов (уже начатых + еще не завершенных + имеющих установленный флаг Ready)  
  ```shell
  curl -X GET http://127.0.0.1:8000/api/v1/active_polls/
  ```
- **GET /active_polls/\<id\>/**  
  Получение опроса по ID со всеми его вопросами  
  ```shell
  curl -X GET http://127.0.0.1:8000/api/v1/active_polls/2/
  ```
- **POST /answer/**  
  Отправка ответа на вопрос. Требуется аутентификация  
  Параметры:
  - `question` - ID целевого вопроса
  - `text` - текст ответа (string). Только для вопросов типа "Ответ текстом"
  - `option` - ID варианта ответа либо несколько ID, разделенных запятыми (string). Только для вопросов с вариантами ответа  
  ```shell
  curl -X POST http://127.0.0.1:8000/api/v1/answer/ --data "question=25&option=41,43" -H "Authorization:Token token_value"
  ```
- **GET /my_polls/**  
  Получение развернутого списка пройденных опросов. Требуется аутентификация
  ```shell
  curl -X GET http://127.0.0.1:8000/api/v1/my_polls/ -H "Authorization:Token token_value"
  ```

