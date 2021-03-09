import requests
from typing import Union
from bs4 import BeautifulSoup

from config import Config


def get_vacancies(search_query: str = "Junior Python", page: int = 0, page_max_count: int = 100,
                  area_id: int = 2, search_period: int = 7) -> Union[dict, requests.Response]:
    """
    Запрос на поиск вакансий по заданным параметрам

    :param search_query: Наименование искомой вакансии
    :param page: Номер страницы
    :param page_max_count: Количество результатов на странице
    :param area_id: Идентификатор города или региона
    :param search_period: Период в днях, по умолчанию 7
    :return: Возвращает ответ сырой ответ от hh.ru
    """
    params = {
        "area": area_id,
        "search_period": search_period,
        "st": "searchVacancy",
        "page": page,
        "items_on_page": page_max_count,
        "text": search_query,
        "clusters": True,
        "enable_snippets": True
    }

    res = requests.get(Config.HH_VACANCY_URL, params=params, headers=Config.HH_REQUEST_HEADERS)

    if res.status_code != 200:
        print("Не удалось выполнить запрос. Ответ от сервиса: %s" % res.content.decode("utf-8"))
        return {}
    else:
        return res


def get_vacancies_from_response(response_obj: requests.Response) -> dict:
    """
    Получение списка вакансий со ссылками

    :param response_obj: Ответ от hh.ru/search/vacancy
    :return: Словарь, ключами которого являются наименования вакансий,значениями ссылки на вакансии
    """
    vacancies = {}
    soup = BeautifulSoup(response_obj.text, 'html.parser')
    spans = soup.find_all("span", {"class": "resume-search-item__name"})

    for span in spans:
        vacancy_title = span.get_text()
        tag_a = span.find("a")
        if tag_a and vacancy_title:
            raw_link = tag_a.get("href", "")
            if not raw_link:
                continue
            vacancy_link = raw_link.split("?query")
            if not vacancy_link:
                continue

            vacancies[vacancy_title] = vacancy_link[0]
    return vacancies


def full_text_from_vacancy(response):
    results = []
    soup = BeautifulSoup(response.text, 'html.parser')
    vacancy_section = soup.find_all("div", {"class": "bloko-gap bloko-gap_bottom"})
    title = soup.find_all("div", {"class": "vacancy-title"})
    results += list(title)
    for x in vacancy_section:
        #print(x.get_text())

        body = x.find_all("div", {"class": "vacancy-section"})
        if not body:
            continue

        results += body
        address = x.find_all("div", {"class": "vacancy-address-text"})
        print("=" * 50)


        #metro = address.find("span", {"class": "bloko-metro-pin"})
        #print(str(address.get_text()))
        #l.append(f"<h2>Адрес: </h2><span>{address.get_text()}</span>")

        #print(x.__dict__)
        #main_skills = x.find('div', class_='bloko-tag-list')
        #print(main_skills.parent.parent.decompose())
        #main_skills.decompose()
        #print(a.get_text())
        return results
        #print(x)
        #print(x.__dict__)
    return results


if __name__ == '__main__':
    count = 0
    while count <= 10:
        response = get_vacancies(page=count)
        results = get_vacancies_from_response(response_obj=response)
        for k, x in enumerate(results.values()):
            res = requests.get(url=x, headers=Config.HH_REQUEST_HEADERS)
            # print(k, res.text)
            r = full_text_from_vacancy(res)
            with open("index.html", "w") as file:
                file.write(" ".join([str(x) for x in r]))
            break
        count += 1
        break
    # print(results)
