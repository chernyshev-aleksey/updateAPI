from bs4 import BeautifulSoup
from typing import Union
import time
import requests

from .config import config, logger


def get_csrftoken(session: requests.Session) -> str:
    response = session.get(
        'https://umschool.net/predbannik/massload/export-purchases/', headers={'user-agent': 'umschool_app'})

    if response.status_code == 200:
        return response.text.split('name="csrfmiddlewaretoken" value="')[1].split('">')[0]
    else:
        time.sleep(1)
        return get_csrftoken(session)


def check_result(session, numb_request, numb_page: int = 1, number_of_repetitions: int = 0) -> str:
    result_request_get = session.get(f'https://umschool.net/predbannik/massload/export-purchases/?page={numb_page}',
                                     headers={
                                         'referer': 'https://umschool.net/predbannik/massload/export-purchases/',
                                         'user-agent': 'umschool_app',
                                     })

    soup1 = BeautifulSoup(result_request_get.text, 'html.parser')
    raw_request_sheet = soup1.find('tbody').find_all('tr')

    request_sheet = []
    for raw_request in raw_request_sheet:
        result = {'number': str(raw_request).split('<td>')[1].split('</td>')[0],
                  'name': str(raw_request).split('<br/><b>')[1].split('</b><br/>')[0]}
        try:
            res = str(raw_request).split('href="')[1].split('">')[0]
        except IndexError:
            res = None
        result['link'] = res
        request_sheet.append(result)

    for results in request_sheet:
        if numb_request == results['number']:
            if results['link'] is not None:
                return results['link']
            else:
                time.sleep(60)
                number_of_repetitions += 1
                if number_of_repetitions >= 60:
                    return None
                else:
                    return check_result(session, numb_request, numb_page, number_of_repetitions)
    return check_result(session, numb_request, numb_page + 1, number_of_repetitions)


def get_post(session, csrftoken, _time_, types_: str, second: bool = False) -> Union[None, str]:
    if types_ == 'mastergroup':
        result_request = session.post(
            'https://umschool.net/predbannik/massload/export-purchases/',
            headers={
                                          'referer': 'https://umschool.net/predbannik/massload/export-purchases/',
                                          'user-agent': 'umschool_app',
                                      },
            data={
                'csrfmiddlewaretoken': csrftoken,
                'service_type': 'mg',
                'month': '',
                'course_type': '',
                'class_type': '',
                'is_valid': '',
                'rate_plan': '',
                'is_manual': '',
                'export_type': '',
                'status': '',
                'types': 'SITE, REQUISITES, FREE, TRANSFER, STAFF, DELAY, AUTO, GIFT, SUBSCRIPTION',
                'pack': '',
                'pack_settings': 'all',
                'utm_source': '',
                'utm_campaign': '',
                'utm_medium': '',
                'utm_content': '',
                'date_from': _time_['start'],
                'date_due': _time_['stop'],
                'export_mode': 'default',
                'product_date_from': '',
                'product_date_due': '',
                'purchase_period': '',
            })
    else:
        result_request = session.post('https://umschool.net/predbannik/massload/export-purchases/',
                                      headers={
                                          'referer': 'https://umschool.net/predbannik/massload/export-purchases/',
                                          'user-agent': 'umschool_app',
                                      },
                                      data={
                                          'csrfmiddlewaretoken': csrftoken,
                                          'service_type': 'course',
                                          'month': '',
                                          'course_type': '',
                                          'class_type': '',
                                          'is_valid': '',
                                          'rate_plan': '',
                                          'is_manual': '',
                                          'export_type': '',
                                          'status': '',
                                          'types': 'SITE,REQUISITES,TRANSFER,STAFF,DELAY',
                                          'pack': '',
                                          'pack_settings': 'all',
                                          'utm_source': '',
                                          'utm_campaign': '',
                                          'utm_medium': '',
                                          'utm_content': '',
                                          'date_from': _time_['start'],
                                          'date_due': _time_['stop'],
                                          'export_mode': 'default',
                                          'product_date_from': '',
                                          'product_date_due': '',
                                          'purchase_period': '',
                                      })

    if 'Упс... Что-то пошло не так' in result_request.text:
        logger.error('error data requests')
        if second:
            return None
        else:
            return get_post(types_, True)

    soup = BeautifulSoup(result_request.text, 'html.parser')
    return soup.find('tbody').find('tr').find('td').string


def download(time_: dict, types: str) -> bool:
    session = requests.Session()
    csrftoken = get_csrftoken(session)

    result_login = session.post('https://umschool.net/predbannik/login/?next=/predbannik/massload/export-purchases/',
                                headers={'user-agent': 'umschool_app',
                                         'referer': 'https://umschool.net/predbannik/login/' +
                                                    '?next=/predbannik/massload/export-purchases/'},
                                data={
                                    "csrfmiddlewaretoken": csrftoken,
                                    "username": config.ADMIN_LOGIN,
                                    "password": config.ADMIN_PASSWORD,
                                    "next": '/predbannik/massload/export-purchases/'})

    if "Добро пожаловать" in result_login.text:
        logger.success("Авторизация прошла успешно")
        csrftoken = result_login.text.split('name="csrfmiddlewaretoken" value="')[1].split('">')[0]
    elif 'Пожалуйста, введите корректные имя пользователя и пароль учётной записи.' in result_login.text:
        logger.error("Ошибка авторизации")
        return

    def get_link():
        numb_request_ = get_post(session=session, csrftoken=csrftoken, _time_=time_, types_=types)
        link_ = check_result(session=session, numb_request=numb_request_)
        if link_ is None:
            return get_link()
        else:
            return link_

    link = get_link()

    filename = f"{time_['start']}-{time_['stop']}.csv"
    r = requests.get(link, allow_redirects=True)
    with open(f"download_files/{types}/{filename}", 'wb') as file:
        file.write(r.content)
        logger.success("Файл успешно скачан")
