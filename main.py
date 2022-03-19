import sys
from io import BytesIO

import requests
from PIL import Image

# Этот класс поможет нам сделать картинку из потока байт

# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:

toponym_to_find = " ".join(sys.argv[1:])
map_api_server = "http://static-maps.yandex.ru/1.x/"

def get_coord(name):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": name,
        "format": "json"
    }
    # Выполняем запрос.
    response = requests.get(geocoder_request, params=params)
    print(response)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = \
        json_response["response"]["GeoObjectCollection"]["featureMember"][0][
            "GeoObject"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        # Печатаем извлечённые из ответа поля:
        return toponym_coodrinates
    raise ValueError("Неверный запрос\nПример: python search.py Москва, ул. Ак. Королева, 12")


def find():
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    address_ll = toponym_to_find
    if toponym_to_find and not toponym_to_find.split(",")[0].isdigit():
        address_ll = ",".join(get_coord(toponym_to_find).split())
    search_params = {
        "apikey": api_key,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    if response:
        display(response, address_ll)
    else:
        raise ValueError(
            "Неверный запрос\nПример: python search.py Москва, ул. Ак. Королева, 12")


def display(response, address_ll):
    json_response = response.json()
    # Получаем первую найденную организацию.
    organization = json_response["features"][0]

    # Получаем координаты ответа.
    point = organization["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    delta = "0.007"

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        # позиционируем карту центром на наш исходный адрес
        # "ll": address_ll,
        # "spn": ",".join([delta, delta]),
        "l": "map",
        # добавим точку, чтобы указать найденную аптеку
        "pt": f"{org_point},pm2al~{address_ll},org"
    }
    get_info(organization)
    response = requests.get(map_api_server, params=map_params)
    Image.open(BytesIO(
        response.content)).show()


def get_info(organization):
    src = [("Адрес", "address"), ("Время", "Hours"), ("Название", "name")]
    for el, name in src:
        if name != 'Hours':
            print(el, organization["properties"]["CompanyMetaData"][name])
        else:
            print(el, organization["properties"]["CompanyMetaData"][name]["text"])


if __name__ == "__main__":
    find()