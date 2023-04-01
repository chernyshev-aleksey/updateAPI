from .scheme import UserPay, Pay
from .config import logger, config
from .database import db, User, MasterGroup, Course
from .download import download

import pandas as pd


class Parse:
    def __init__(self, dataframe):
        self.value = dataframe.where(pd.notnull(dataframe), None).values
        title = list(dataframe)
        self.SITE_ID_NUMBER = title.index('USERID')
        self.SITE_LOGIN_NUMBER = title.index('Username')
        self.FULL_NAME_NUMBER = title.index('ФИО')
        self.VK_ID_NUMBER = title.index('VK ID')
        self.EMAIL_NUMBER = title.index('Email')
        self.PAID_COST_NUMBER = title.index('Сумма')
        self.PRODUCT_NUMBER = title.index('Услуга')
        self.SUBJECT_NUMBER = title.index('Предмет')
        self.CLASS_NUMBER = title.index('Год')
        self.DATA_CREATED_NUMBER = title.index('Дата создания')
        self.DATA_PAID_NUMBER = title.index('Дата оплаты')
        self.VALID_NUMBER = title.index('Покупка валидна')
        self.TYPE_PAY_NUMBER = title.index('Тип')

    def get_dict(self, number):
        pay = Pay.parse_obj({
            "site_id": self.value[number][self.SITE_ID_NUMBER],
            "site_login": self.value[number][self.SITE_LOGIN_NUMBER],
            "full_name": self.value[number][self.FULL_NAME_NUMBER],
            "vk_id": self.value[number][self.VK_ID_NUMBER],
            "vk_name": self.value[number][self.VK_ID_NUMBER],
            "email": self.value[number][self.EMAIL_NUMBER],
            "paid_cost": self.value[number][self.PAID_COST_NUMBER],
            "product": self.value[number][self.PRODUCT_NUMBER],
            "subject": self.value[number][self.SUBJECT_NUMBER],
            "class_": self.value[number][self.CLASS_NUMBER],
            "data_created": self.value[number][self.DATA_CREATED_NUMBER],
            "data_paid": self.value[number][self.DATA_PAID_NUMBER],
            "valid": self.value[number][self.VALID_NUMBER],
            "type_pay": self.value[number][self.TYPE_PAY_NUMBER]
        })
        return pay

    def get_site_id(self, number):
        return self.value[number][self.SITE_ID_NUMBER]

    def get_subject_key(self, number):
        return f"{self.value[number][self.SUBJECT_NUMBER]} {self.value[number][self.DATA_CREATED_NUMBER]}"


__all__ = ['UserPay', 'logger', 'db', 'config', 'User', 'MasterGroup', 'download', 'Parse', 'Course']
