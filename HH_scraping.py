import json
import requests
import pandas as pd

# Урок 2. Парсинг данных. HTML, DOM, XPath
# Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы получаем должность)
# с сайтов HH(обязательно) и/или Superjob(по желанию). Приложение должно анализировать несколько страниц сайта (также вводим
# через input или аргументы). Получившийся список должен содержать в себе минимум:
#
#     Наименование вакансии.
#     Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
#     Ссылку на саму вакансию.
#     Сайт, откуда собрана вакансия. (можно прописать статично hh.ru или superjob.ru)
#
# По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть одинаковая
# для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.

# Пользователь вводит название интересующей его вакансии:
position = input('Какая должность вас интересует? ')


def getPage(page=0):
    """
    Запрашиваем информацию через API сайта.
    :param page: Получаем параметры только для вакансий, в названии которых есть сочетание, указанное пользователем.
    :return: Получаем список вакансий и их параметры.
    """
    url = 'https://api.hh.ru/vacancies'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
    params = {
        'text': f'NAME:{position}',
        'page': page,
        'per_page': 100
    }
    session = requests.Session()
    response = session.get(url, headers=headers, params=params)
    data = response.content.decode()
    response.close()
    return data


def getJson():
    """
    Преобразуем полученный текст в файл JSON для заданного количества страниц. Скорее всего, их не будет более 20, поэтому оставляем 20 страниц.
    :return: Получаем файл JSON с нужными вакансиями.
    """
    for page in range(0, 20):
        jsObj = json.dumps(getPage(page))
        return json.loads(json.loads(jsObj))


dictionary = {'Наименование вакансии': [], 'Зарплата, верхняя планка': [], 'Зарплата, нижняя планка': [], 'Валюта': [], 'Ссылка': [], 'Источник': []}

for i in getJson()['items']:
    """
    Записываем интересующую нас информацию в словарь.
    """
    for key, value in i.items():
        if key == 'name':
            dictionary['Наименование вакансии'].append(value)
            dictionary['Источник'].append('HeadHunter')
        if key == 'salary':
            try: # Благодаря структуре try-except были учтены возможные пропуски в данных.
                dictionary['Зарплата, верхняя планка'].append(value['to'])
                dictionary['Зарплата, нижняя планка'].append(value['from'])
                dictionary['Валюта'].append(value['currency'])
            except TypeError:
                dictionary['Зарплата, верхняя планка'].append(None)
                dictionary['Зарплата, нижняя планка'].append(None)
                dictionary['Валюта'].append(None)
        if key == 'alternate_url':
            dictionary['Ссылка'].append(value)

# Создаем датафрейм:
df = pd.DataFrame(dictionary)

# Делаем запись в файл:
df.to_csv('HH_scraping.csv')