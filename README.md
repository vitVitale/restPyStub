## REST PY STUB ##

#### Подготовка: ####

* наличие Python 3.10(python --version)
* настройте интерпретатор Python
* pip3 install -r requirements.txt
* export TIMEOUT=10  (таймаут на ответ)
* uvicorn main:app --reload  (Запуск сервиса)

#### Установка в k8s ####

* cd _charts
* helm package py-stub
* helm install py-stub ./py-stub-1.1.0.tgz

#### Интерактивная документация: ####

* swagger -> http://127.0.0.1:8000/docs
* another doc -> http://127.0.0.1:8000/redoc


## Пример использования с cURL
#### Создание заглушки на ендпоинт [some/endpoint/delivery]
curl -X PUT 'http://localhost:8000/define_stub?url=some/endpoint/delivery' \
-H 'Content-Type: application/json' \
-d '{ "status": 201, "body": { "sla": "double", "minimalAmount": 3600}}'

#### Использование заглушки по [some/endpoint/delivery]
curl -X POST 'http://localhost:8000/stub/some/endpoint/delivery' \
-H 'Content-Type: application/json' \
-d '{ "statuses": "qdoda" }'

curl -X PUT 'http://localhost:8000/stub/some/endpoint/delivery?q=mySuperQuery&isa=505' \
-H 'Content-Type: text/plain' \
-d 'SOME TEXT'

#### Просмотр запросов по всем эндпоинтам
curl -X GET 'http://127.0.0.1:8000/requests' \
-H 'accept: application/json'

#### Просмотр последнего запроса по [some/endpoint/delivery] полностью
curl -X GET 'http://127.0.0.1:8000/request/some/endpoint/delivery' \
-H 'accept: application/json'

#### Просмотр последнего запроса по [some/endpoint/delivery] с уточнениями (body|headers|params|method)
curl -X GET 'http://127.0.0.1:8000/request/some/endpoint/delivery?fetch=body' \
-H 'accept: application/json'
