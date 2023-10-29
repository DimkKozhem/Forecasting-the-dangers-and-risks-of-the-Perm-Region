# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import folium
import pandas as pd
import json
from datetime import date, timedelta

app = Flask(__name__)

with open('boundary-polygon-lvl6.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

data = pd.read_csv("zkh_fire_dtp_predict.csv")

def generate_dates(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)

def get_value_for_region_and_date(region, date, category):
    try:
        value = data[(data['region'] == region) & (data['date'] == date)][f'pred_{category}'].values[0]
        return value
    except IndexError:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    m = folium.Map(location=[58.0, 56.3], zoom_start=10)

    date_range = list(generate_dates(date(2022, 9, 1), date(2022, 12, 31)))
    selected_date = request.form.get('date') if request.method == "POST" else str(date_range[0])

    style_function = lambda x: {
        'fillColor': '#ffffff',
        'color': '#000000',
        'weight': 2,
        'fillOpacity': 0.6
    }

    folium.GeoJson(
        geojson_data,
        name="Районы",
        style_function=style_function,
        tooltip=folium.features.GeoJsonTooltip(fields=['NAME'], labels=False, sticky=False)
    ).add_to(m)

    zkh_group = folium.FeatureGroup(name='ЖКХ')
    fire_group = folium.FeatureGroup(name='Пожары')
    dtp_group = folium.FeatureGroup(name='ДТП')

    # список координат с названиями
    locations = [
        ("Чердынский ГО", [60.84687140820415, 56.739301517160555]),
        ("Красновишерский ГО", [60.5171516035975, 58.28112527839618]),
        ("Соликамский ГО", [59.80990122340786, 56.709652535478526]),
        ("Александровский МО", [59.41736034964531, 57.83448371612613]),
        ("Гайнский МО", [60.538204696462564, 53.59398796666738]),
        ("Косинский МО", [59.904297871072835, 55.02599448608207]),
        ("Кочевский МО", [59.74129286128167, 54.203659509825115]),
        ("Юрлинский МО", [59.408773936434976, 54.076976886022706]),
        ("Кудымкарский МО", [59.03903691369914, 54.53856265246462]),
        ("Юсьвинский МО", [59.05338733552489, 55.531326172164114]),
        ("Ильинский ГО", [58.6439169884118, 55.764833510415585]),
        ("Карагайский МО", [58.47793063246226, 55.01830766455154]),
        ("Сивинский МО", [58.47783073895963, 54.20432233938981]),
        ("Верещагинский ГО", [58.12483952748204, 54.39674206409326]),
        ("Лысьвенский ГО", [57.905835245057936, 57.999701923252225]),
        ("Горнозаводский ГО", [58.58060833404941, 58.67433285289662]),
        ("Чусовской ГО", [58.3178330538493, 57.429028323901996]),
        ("ГО город Кизел", [59.0896854130792, 58.11767100111628]),
        ("Добрянский ГО", [58.62468817847794, 56.67172061774788]),
        ("Березовский МО", [57.63270154552351, 57.54567482205953]),
        ("Очерский ГО", [57.89232107638927, 54.621979761932664]),
        ("Нытвенский ГО", [58.113549647593544, 55.36481427184353]),
        ("Кунгурский МО", [57.47661808154046, 56.61082340582531]),
        ("Кишертский МО", [57.33949890776749, 57.598936349666424]),
        ("Оханский ГО", [57.65829770008185, 55.213222519622505]),
        ("Большесосновский МО", [57.54085693627111, 54.45311311007274]),
        ("Чайковский ГО", [56.70827330863123, 54.35548707554191]),
        ("Суксунский ГО", [57.079748514457805, 57.499179046535396]),
        ("Ординский МО", [57.081017893173275, 56.779631230117474]),
        ("Уинский МО", [56.87248837106554, 56.48375763762739]),
        ("Чернушинский ГО", [56.54101538902518, 56.17518334042142]),
        ("Октябрьский ГО", [56.49879831873498, 56.95678904181498]),
        ("Куединский МО", [56.53776738937279, 55.208384221562596]),
        ("Еловский МО", [56.928680254934264, 54.88274171559331]),
        ("Частинский МО", [57.26488818894044, 54.777299521972495]),
        ("Осинский ГО", [57.270738498441006, 55.49409029950849]),
        ("Бардымский МО", [56.88717605335833, 55.65795259082663]),
        ("Пермский МО", [57.78712407630865, 56.10060328772387]),
        ("Краснокамский ГО", [58.16857481666166, 55.8988765366291]),
        ("Пермский ГО", [58.03608230245032, 56.264713888899614]),
        ("ЗАТО Звёздный", [57.71070360143645, 56.27128964774174]),
        ("ГО город Березники", [59.38624330049317, 56.32532182782306]),
        ("Губахинский ГО", [58.8207021616366, 57.815224646769984])
        # Ваш список координат с названиями
        # Продолжение список для всех регионов
    ]

    # Данные для списка рядом с картой
    list_data = []

    # Добавление маркеров для каждой локации
    for name, location in locations:
        zkh_value = get_value_for_region_and_date(name, selected_date, 'zkh')
        fire_value = get_value_for_region_and_date(name, selected_date, 'fire')
        dtp_value = get_value_for_region_and_date(name, selected_date, 'dtp')

        if zkh_value is not None:
            zkh_value_percentage = round(zkh_value * 100, 2)
            marker = folium.Marker(
                location=location,
                tooltip=f"{name}: {zkh_value_percentage}% вероятность аварии",
                icon=folium.Icon(icon="wrench", color="yellow", prefix="fa")
            )
            marker.add_to(zkh_group)
            list_data.append((name, 'ЖКХ', zkh_value_percentage))

        if fire_value is not None:
            fire_value_percentage = round(fire_value * 100, 2)
            marker = folium.Marker(
                location=[location[0], location[1] - 0.15],  # Смещение маркера влево
                tooltip=f"{name}: {fire_value_percentage}% вероятность пожара",
                icon=folium.Icon(icon="fire", color="red", prefix="fa")
            )
            marker.add_to(fire_group)
            list_data.append((name, 'Пожары', fire_value_percentage))

        if dtp_value is not None:
            dtp_value_percentage = round(dtp_value * 100, 2)
            marker = folium.Marker(
                location=[location[0], location[1] + 0.15],  # Смещение маркера вправо
                tooltip=f"{name}: {dtp_value_percentage}% вероятность ДТП",
                icon=folium.Icon(icon="car-crash", color="blue", prefix="fa")
            )
            marker.add_to(dtp_group)
            list_data.append((name, 'ДТП', dtp_value_percentage))

            # Создание списка с общей информацией
            common_info_list = [f"{name} - {category}: {value}%" for name, category, value in list_data]

            def list_to_two_column_html(data_list):
                html_content = "<table>"

                # Разбиваем список на пары
                for i in range(0, len(data_list), 3):
                    item1 = data_list[i]
                    # Проверяем, есть ли следующий элемент
                    item2 = data_list[i + 1] if i + 1 < len(data_list) else ""
                    html_content += f"<tr><td>{item1}</td><td>{item2}</td></tr>"

                html_content += "</table>"
                return html_content

            common_info_html = list_to_two_column_html(common_info_list)

            # Определение местоположения для общего маркера
            common_marker_location = [58.5, 60.5]

            # Добавление общего маркера
            folium.Marker(
                location=common_marker_location,
                tooltip=common_info_html,
                icon=folium.Icon(color='green', icon='info-sign')
            ).add_to(m)

    zkh_group.add_to(m)
    fire_group.add_to(m)
    dtp_group.add_to(m)
    folium.LayerControl().add_to(m)

    return render_template("index.html", map=m._repr_html_(), date_range=date_range, selected_date=selected_date, list_data=list_data)

if __name__ == "__main__":
    app.run(debug=True)
