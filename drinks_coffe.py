import os
import json
import requests
import folium
import logging
from geopy import distance
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()

    places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not places:
        return None

    most_relevant = places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lat), float(lon)


def load_cafes(filename):
    with open(filename, "r", encoding="cp1251") as coffee_file:
        return json.load(coffee_file)


def distances(user_coords, cafes):
    cafes_distance = []
    for cafe in cafes:
        name = cafe["Name"]
        lat = float(cafe["Latitude_WGS84"])
        lon = float(cafe["Longitude_WGS84"])
        dist = distance.distance(user_coords, (lat, lon)).km
        cafes_distance.append({
            'title': name,
            'latitude': lat,
            'longitude': lon,
            'distance': dist
        })
    return cafes_distance

def build_map(user_coords, nearest_cafes, filename="map.html"):
    m = folium.Map(location=user_coords)

    folium.Marker(
        location=user_coords,
        popup="Вы здесь",
        icon=folium.Icon(icon="user"),
    ).add_to(m)

    for cafe in nearest_cafes:
        folium.Marker(
            location=(cafe['latitude'], cafe['longitude']),
            popup=f"{cafe['title']}",
            icon=folium.Icon(color="green"),
        ).add_to(m)

    m.save(filename)
    logging.info(f"Карта сохранена в файле {filename}")


def main():
    apikey = os.getenv("YANDEX_API_KEY")
    location = input('Ваше местоположение: ')
    user_coords = fetch_coordinates(apikey, location)

    cafes = load_cafes("coffee.json")
    cafes_with_distance = distances(user_coords, cafes)
    nearest_cafes = sorted(cafes_with_distance, key=lambda cafe: cafe['distance'])[:5]


    build_map(user_coords, nearest_cafes, filename="map.html")


if __name__ == "__main__":
    main()