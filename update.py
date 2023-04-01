import asyncio
import fnmatch
import os
import argparse

import datetime
import pandas as pd
import requests

from asyncpg import ForeignKeyViolationError, UniqueViolationError

from src import UserPay, User, MasterGroup, download, logger, db, config, Parse, Course


async def update_course(_file):
    await db.set_bind(config.DSN)
    await db.gino.create_all()

    count_product = 0
    add_count = 0
    not_add_count = 0

    parse = Parse(pd.read_csv(f"download_files/course/{_file}", delimiter=',', low_memory=False))

    for number_payment in range(len(parse.value)):
        item = parse.get_dict(number_payment)
        try:
            try:
                await Course.create(
                    site_id=int(item.site_id),
                    paid_cost=item.paid_cost,
                    product=item.product,
                    subject=item.subject,
                    _class=item.class_,
                    data_created=item.data_created,
                    data_paid=item.data_paid,
                    valid=item.valid,
                    unique_code="{site_id} {full_price} {full_service} {valid}".format(
                        site_id=item.site_id,
                        full_price=item.paid_cost,
                        full_service=item.product,
                        valid=item.valid),
                    type_pay=item.type_pay
                )
            except UniqueViolationError:
                not_add_count += 1
                logger.log('error_update', "{site_id}: {full_service}, {full_price}, {valid}".format(
                        site_id=item.site_id,
                        full_price=item.paid_cost,
                        full_service=item.product,
                        valid=item.valid))
            else:
                add_count += 1
                logger.log('update', "{site_id}: {full_service}, {full_price}, {valid}".format(
                        site_id=item.site_id,
                        full_price=item.paid_cost,
                        full_service=item.product,
                        valid=item.valid))
        except ForeignKeyViolationError:
            try:
                id_vk = int(item.vk_id)
            except TypeError:
                id_vk = None

            await User.create(
                site=int(item.site_id),
                id_vk=id_vk,
                vk_name=item.vk_name,
                site_login=item.site_login,
                full_name=item.full_name,
                email=item.email
            )

            await Course.create(
                    site_id=int(item.site_id),
                    paid_cost=item.paid_cost,
                    product=item.product,
                    subject=item.subject,
                    _class=item.class_,
                    data_created=item.data_created,
                    data_paid=item.data_paid,
                    valid=item.valid,
                    unique_code="{site_id} {full_price} {full_service} {valid}".format(
                        site_id=item.site_id,
                        full_price=item.paid_cost,
                        full_service=item.product,
                        valid=item.valid),
                    type_pay=item.type_pay
                )
            add_count += 1
            logger.log('update', "{site_id}: {full_service}, {full_price}, {valid}".format(
                site_id=item.site_id,
                full_price=item.paid_cost,
                full_service=item.product,
                valid=item.valid))

    requests.get(
        f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage",
        params={'chat_id': config.ADMIN, 'disable_notification': True,
                'text': f"""
БД обновилось (Мастер-группы)
В файле продуктов-{count_product}

Добавленное в бд продуктов-{add_count}
Не добавлено продуктов-{not_add_count}"""})


async def update_mastergroup(_file):
    await db.set_bind(config.DSN)
    await db.gino.create_all()

    parse = Parse(pd.read_csv(f"download_files/mastergroup/{_file}", delimiter=',', low_memory=False))

    sorted_info = {}
    for number_pay in range(len(parse.value)):
        try:
            sorted_info[parse.get_site_id(number_pay)]

        except KeyError:
            # Пользователя ещё нет
            sorted_info[parse.get_site_id(number_pay)] = {}
            sorted_info[parse.get_site_id(number_pay)][parse.get_subject_key(number_pay)] = [parse.get_dict(number_pay)]
        else:
            # Пользователь есть
            try:
                sorted_info[parse.get_site_id(number_pay)][parse.get_subject_key(number_pay)]
            except KeyError:
                sorted_info[parse.get_site_id(number_pay)][parse.get_subject_key(number_pay)] = \
                    [parse.get_dict(number_pay)]
            else:
                a = sorted_info[parse.get_site_id(number_pay)][parse.get_subject_key(number_pay)]
                a.append(parse.get_dict(number_pay))
                sorted_info[parse.get_site_id(number_pay)][parse.get_subject_key(number_pay)] = a

        list_month = {
            0: "Сентябрь",
            1: "Октябрь",
            2: "Ноябрь",
            3: "Декабрь",
            4: "Январь",
            5: "Февраль",
            6: "Март",
            7: "Апрель",
            8: "Май"
        }

    info = UserPay.parse_obj({"info": sorted_info}).info

    user_count = len(info)
    count_product = 0
    for key_site_id in info.keys():
        count_product += len(info[key_site_id])

    add_count = 0
    not_add_count = 0

    for key_site_id in info.keys():
        for key_subject in info[key_site_id].keys():
            if len(info[key_site_id][key_subject]) != 1:
                mon = ''
                for v in info[key_site_id][key_subject]:
                    mon += v.product
                if ' Май ' in mon and info[key_site_id][key_subject][0].class_ != "10 класс":
                    colvo_mes = str(float(len(info[key_site_id][key_subject])) - 0.5)
                else:
                    colvo_mes = str(len(info[key_site_id][key_subject]))
                _month = 8
                for o in range(9):
                    for u in info[key_site_id][key_subject]:
                        if list_month[o] in u.product:
                            if o < _month:
                                _month = o
                month_ = 0
                for o in range(9):
                    for u in info[key_site_id][key_subject]:
                        if list_month[o] in u.product:
                            if o > month_:
                                month_ = o
                months = f'{(list_month[_month]).lower()}-{(list_month[month_]).lower()}'
                service = str(info[key_site_id][key_subject][0].product.split(') ')[0])
                service = service[0].lower() + service[1:]
                if float(colvo_mes) >= 5.0:
                    full_service = f'Пакет {service}) {colvo_mes} месяцев {months}'
                else:
                    full_service = f'Пакет {service}) {colvo_mes} месяца {months}'
                full_price = 0
                for u in info[key_site_id][key_subject]:
                    full_price += int(u.paid_cost)
            else:
                full_price = info[key_site_id][key_subject][0].paid_cost
                full_service = info[key_site_id][key_subject][0].product
            user_item = info[key_site_id][key_subject][0]
            try:
                try:
                    await MasterGroup.create(
                        site_id=int(user_item.site_id),
                        paid_cost=full_price,
                        product=full_service,
                        subject=user_item.subject,
                        _class=user_item.class_,
                        data_created=user_item.data_created,
                        data_paid=user_item.data_paid,
                        valid=user_item.valid,
                        unique_code=f"{user_item.site_id} {full_price} {full_service} {user_item.valid}",
                        type_pay=user_item.type_pay
                    )
                except UniqueViolationError:
                    not_add_count += 1
                    logger.log('error_update', "{site_id}: {full_service}, {full_price}, {valid}".format(
                        site_id=user_item.site_id,
                        full_service=full_service,
                        full_price=full_price,
                        valid=user_item.valid
                    ))
                else:
                    add_count += 1
                    logger.log('update', "{site_id}: {full_service}, {full_price}, {valid}".format(
                        site_id=user_item.site_id,
                        full_service=full_service,
                        full_price=full_price,
                        valid=user_item.valid
                    ))
            except ForeignKeyViolationError:
                try:
                    id_vk = int(user_item.vk_id)
                except TypeError:
                    id_vk = None

                await User.create(
                    site=int(user_item.site_id),
                    id_vk=id_vk,
                    vk_name=user_item.vk_name,
                    site_login=user_item.site_login,
                    full_name=user_item.full_name,
                    email=user_item.email
                )

                await MasterGroup.create(
                    site_id=int(user_item.site_id),
                    paid_cost=full_price,
                    product=full_service,
                    subject=user_item.subject,
                    _class=user_item.class_,
                    data_created=user_item.data_created,
                    data_paid=user_item.data_paid,
                    valid=user_item.valid,
                    unique_code=f"{user_item.site_id} {full_price} {full_service} {user_item.valid}",
                    type_pay=user_item.type_pay
                )
                add_count += 1
                logger.log('update', "{site_id}: {full_service}, {full_price}, {valid}".format(
                    site_id=user_item.site_id,
                    full_service=full_service,
                    full_price=full_price,
                    valid=user_item.valid
                ))
    requests.get(
        f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage",
        params={'chat_id': config.ADMIN, 'disable_notification': True,
                'text': f"""
БД обновилось (Мастер-группы)
В файле пользователей-{user_count}, продуктов-{count_product}

Добавленное в бд продуктов-{add_count}
Не добавлено продуктов-{not_add_count}"""})


def createParser():
    _parser = argparse.ArgumentParser()
    _parser.add_argument('--not_download', action='store_const', const=True)
    _parser.add_argument('--not_remove', action='store_const', const=True)
    return _parser


@logger.catch(level="ERROR")
def main():
    parser = createParser()
    namespace = parser.parse_args()

    if not namespace.not_download:
        date = datetime.datetime.now()
        start_data = (date - datetime.timedelta(hours=1)).strftime('%d.%m.%Y %H')
        stop_data = date.strftime('%d.%m.%Y %H')
        download({
            "start": f"{start_data}:00",
            "stop": f"{stop_data}:00"
        }, 'mastergroup')
        download({
            "start": f"{start_data}:00",
            "stop": f"{stop_data}:00"
        }, 'course')

    for file_name in os.listdir(f"download_files/mastergroup"):

        if fnmatch.fnmatch(file_name, '*.csv'):

            asyncio.run(update_mastergroup(file_name))
            if not namespace.not_remove:
                os.remove(f"download_files/mastergroup/{file_name}")

    for file_name in os.listdir(f"download_files/course"):

        if fnmatch.fnmatch(file_name, '*.csv'):

            asyncio.run(update_course(file_name))
            if not namespace.not_remove:
                os.remove(f"download_files/course/{file_name}")


if __name__ == '__main__':
    main()
