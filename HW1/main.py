import json
from math import factorial
from http import HTTPStatus
from urllib.parse import parse_qs

# запустить приложение: uvicorn main:app --reload
# запустить тесты: pytest test_homework_1.py

# Приложение
async def app(scope, receive, send) -> None:
    assert scope['type'] == 'http'

    if scope["method"] == "GET":
        if scope["path"].startswith("/factorial"):
            return await get_factorial(scope, send)
        elif scope["path"].startswith("/fibonacci"):
            return await get_fibonacci(scope, send)
        elif scope["path"].startswith("/mean"):
            return await get_mean(receive, send)
        else:
            return await response(send, HTTPStatus.NOT_FOUND, {"error": "Not Found"})
    else:
        return await response(send, HTTPStatus.NOT_FOUND, {"error": "Not Found"})


# Факториал
async def get_factorial(scope, send):
    query_string = scope.get('query_string', b'').decode('utf-8')
    params = parse_qs(query_string)
    values = params.get("n")
    if not values:
        return await response(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error": "Unprocessable Entity"})
    else:
        try:
            n = int(values[0])
        except:
            return await response(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error": "Unprocessable Entity"})
        if n < 0:
            return await response(send, HTTPStatus.BAD_REQUEST, {"error": "Bad Request"})
        else:
            # ищем факториал
            result = factorial(n)
            return await response(send, HTTPStatus.OK, {"result": result})


# Фибоначчи
async def get_fibonacci(scope, send):
    pieces = scope["path"].split('/')
    if len(pieces) != 3:
        return await response(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error": "Unprocessable Entity"})
    try:
        n = int(pieces[2])
    except:
        return await response(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error": "Unprocessable Entity"})

    a = 0
    b = 1
    if n < 0:
        return await response(send, HTTPStatus.BAD_REQUEST, {"error": "Bad Request"})
    # ищем Фибоначчи
    elif n == 0 or n == 1:
        result = n
    else:
        for i in range(1, n):
            c = a + b
            a = b
            b = c
        result = b
    return await response(send, HTTPStatus.OK, {"result": result})


# Среднее арифметическое
async def get_mean(receive, send):
    try:
        message = await receive()
        n = json.loads(message.get('body'))
        if not n:
            return await response(send, HTTPStatus.BAD_REQUEST, {"error": "Bad Request"})
        elif not isinstance(n, list):
            return await response(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error": "Unprocessable Entity"})
        elif not all(isinstance(item, (int, float)) for item in n):
            return await response(send, HTTPStatus.BAD_REQUEST, {"error": "Bad Request"})
        else:
            result = sum(n) / len(n)
            return await response(send, HTTPStatus.OK, {"result": result})
    except:
        return await response(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error": "Unprocessable Entity"})


# Отправляем ответ
async def response(send, status_code, response_data):
    response_body = json.dumps(response_data).encode('utf-8')
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [
            (b'content-type', b'application/json')
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': response_body,
    })
