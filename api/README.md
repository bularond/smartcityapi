# Events API

API получения доступа к различным событиям города.

| Метод | Шаблон                              | Возвращаемая информция|
|:-----:|:-----------------------------------:|:---------------------:|
| GET   | www.{hostname}.com/api/event_types  | db.event_type_list    |
| GET   | www.{hostname}.com/api/event/params |                       |

# Параметры
| Название       | Количество | Тип информации | Шаблон           |
|:-------------- |:----------:|:--------------:|:----------------:|
| type           | 1+         | string         | "energy","water" |
| begin_interval | 2          | datetimes      |                  |
| in_area        | 1          | geojson        |                  |
