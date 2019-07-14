#  VK Bot

## Database

| Поле         | Описание                                       | Пример                   |
|:------------ |:---------------------------------------------- |:------------------------ |
| user_id      | id пользователья ВК                            | 16022903                 |
| chat_stage   | Стадия чита. Возможные значения:               |                          |
|              | Одидание адреса пользователя                   | registaration            |
|              | Выбор полей. Ожидание нажатия кнопки           | pushing                  |
|              | Выбор полей. Ожидание event_type.title         | choise_%type%            |
|              | Выбор дня, за которые надо предупредить        | clarification            |
|              | Регистрация закончена, ожидание сообщений      | waiting                  |
| street       | см. users_mailer                               |                          |
| home         | см. users_mailer                               |                          |
| wish_list    | см. users_mailer                               |                          |
| house_geopos | см. users_mailer                               |                          |
