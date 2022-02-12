import sys
from io import BytesIO

import requests
from PIL import Image

# Этот класс поможет нам сделать картинку из потока байт

# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:

toponym_to_find = " ".join(sys.argv[1:])


def get_coord(name):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": name,
        "format": "json"
    }
    # Выполняем запрос.
    response = requests.get(geocoder_request, params=params)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()

        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = \
        json_response["response"]["GeoObjectCollection"]["featureMember"][0][
            "GeoObject"]
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"][
            "text"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        # Печатаем извлечённые из ответа поля:
        return toponym_coodrinates
    raise ValueError("Неверный запрос")


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

json_response = response.json()
data = []
for i in range(min(10, len(json_response["features"]))):
    organization = json_response["features"][i]
    # Название организации.
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    org_hours = organization["properties"]["CompanyMetaData"].get("Hours", False)
    org_address = organization["properties"]["CompanyMetaData"]["address"]

    # Получаем координаты ответа.
    point = organization["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    if org_hours:
        if org_hours["Availabilities"][0].get("TwentyFourHours", False):
            data.append(("pm2gnl", org_point))
        else:
            data.append(("org", org_point))
    else:
        data.append(("pm2grl", org_point))
    # Адрес организации.
# Собираем параметры для запроса к StaticMapsAPI:
map_params = {
    # позиционируем карту центром на наш исходный адрес
    # "ll": address_ll,
    # "spn": ",".join([delta, delta]),
    "l": "map",
    # добавим точку, чтобы указать найденную аптеку
    "pt": f"{'~'.join([','.join((i[1], i[0])) for i in data])}~{address_ll}"
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
# ... и выполняем запрос
response = requests.get(map_api_server, params=map_params)
print(response.url)
Image.open(BytesIO(
    response.content)).show()