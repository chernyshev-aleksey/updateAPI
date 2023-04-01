from pydantic import BaseModel, validator
from typing import Optional, Union
from datetime import datetime


class Pay(BaseModel):
    site_id: int
    site_login: Union[str, None]
    full_name: Optional[str]
    vk_id: Union[int, str, None]
    vk_name: Union[int, str, None]
    email: Optional[str]
    paid_cost: int
    product: str
    subject: str
    class_: str
    data_created: Union[datetime, str]
    data_paid: Union[datetime, str]
    valid: Union[bool, str]
    type_pay: str

    @validator('site_login')
    def not_none_site_login(cls, v):
        if v is None:
            return '_'
        else:
            return v

    @validator('vk_id')
    def check_vk_id(cls, v):
        if str(v).isdigit():
            return int(v)
        else:
            return None

    @validator('vk_name')
    def check_vk_name(cls, v):
        if str(v).isdigit():
            return None
        else:
            return v

    @validator('valid')
    def check_valid(cls, v):
        if v == 'Да':
            return True
        else:
            return False

    @validator('*')
    def change_nan_to_none(cls, v):
        if v is None:
            return None
        return v

    @validator('data_created', 'data_paid')
    def data_created_validator(cls, data_or_string, values) -> datetime:
        if data_or_string == 'Нет':
            return values['data_created']
        if data_or_string is datetime:
            return data_or_string
        else:
            return datetime.strptime(data_or_string, '%d.%m.%Y %H:%M')


class UserPay(BaseModel):
    info: dict[int, dict[str, list[Pay]]]
