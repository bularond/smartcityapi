import requests
from settings import yandex_geocoder_key


def str_to_geo_data(st):
    """
    : Возвращает dict{'street':str, 'home_number':int, 'geocode': geocode}
    """
    st = '+'.join(st.split())
    respounse = requests.get(url=f"https://geocode-maps.yandex.ru/1.x/?apikey={yandex_geocoder_key}&format=json&geocode={st}")
    json = respounse.json()
    json = json['response']['GeoObjectCollection']['featureMember']
    if(len(json)):
        pass


if __name__ == "__main__":
    str_to_geo_data("Тверская 6")