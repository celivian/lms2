import sys
from io import BytesIO
import requests
from PIL import Image


# Пусть наше приложение предполагает запуск:
# python search.py Москва, ул. Ак. Королева, 12
# Тогда запрос к геокодеру формируется следующим образом:


def get_spn(toponym_to_find):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": toponym_to_find,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        pass
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    x1, y1 = map(float, toponym['boundedBy']['Envelope']['upperCorner'].split(' '))
    x2, y2 = map(float, toponym['boundedBy']['Envelope']['lowerCorner'].split(' '))
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    ll = ','.join([toponym_longitude, toponym_lattitude])
    spn = f'{abs(x2 - x1) / 2.0},{abs(y1 - y2) / 2.0}'
    return ll, spn


def get_map(place, point):
    ll, spn = get_spn(place)
    org_point = "{0},{1}".format(point[0], point[1])
    point = '~'.join([','.join([str(j) for j in i]) for i in point])
    map_params = {
        "ll": ll,
        "spn": spn,
        "l": "map",
        "pt": "{0},pm2dgl".format(point)
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)

    Image.open(BytesIO(
        response.content)).show()

    # Создадим картинку


def getcoords(address):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={address}&format=json"
    # Выполняем запрос.
    response = requests.get(geocoder_request)
    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
        # Получаем первый топоним из ответа геокодера.
        # Согласно описанию ответа, он находится по следующему пути:
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        # return toponym["description"]
        # Полный адрес топонима:
        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        # Координаты центра топонима:
        toponym_coodrinates = toponym["Point"]["pos"]
        # Печатаем извлечённые из ответа поля:
        return ",".join(toponym_coodrinates.split())
    # return fed_okg
    else:
        print("Ошибка выполнения запроса:")
        print(geocoder_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")


def search_organization(name, address_ll):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    search_params = {
        "apikey": api_key,
        "text": name,
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        # ...
        pass
    sp = []
    for i in response.json()['features']:
        sp.append(i['geometry']['coordinates'])
    return sp


if __name__ == '__main__':
    toponym_to_find = " ".join(sys.argv[1:])
    if not toponym_to_find:
        toponym_to_find = input('Введите объект для поиска: ')
    get_map(toponym_to_find, search_organization('аптека', getcoords(toponym_to_find)))
