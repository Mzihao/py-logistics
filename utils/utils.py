import functools
import hashlib
import datetime
import pytz
import time
from importlib import import_module
from sql_app import crud
from settings import TOKEN_LIST
from utils.error_msg import get_error_msg


class CustomError(Exception):
    """自定义一个Rest 请求return错误"""
    status_code = 500

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


def md5_encode(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def get_jwt_token_info(key=None):
    return g.token_info.get(key) if key else g.token_info


def convert_upper_case_to_snake_case(string):
    new_string = ""
    index = 0

    for char in string:
        if index == 0:
            new_string += char.lower()
        elif char.isupper():
            new_string += f"_{char.lower()}"
        else:
            new_string += char

        index += 1

    return new_string


def response_json(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        code, data = f(*args, **kwargs)
        json = {
            "code": code,
            "message": get_error_msg(code),
            "data": data,
        }
        return json

    return decorator


def header_token_required():
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            token = ""
            if token and token in TOKEN_LIST:
                return f(*args, **kwargs)
            else:
                raise CustomError('Missing header request: token required.', status_code=401)

        return wrapper

    return decorator


def auto_import_namespace(namespace):
    """返回指定平台的实现模块
    Args:
        namespace: 字符串
    Returns:
        Namespace
    """
    try:
        namespace_module = import_module(f"app.api.v1.{namespace.lower()}")
        router = getattr(
            namespace_module, 'router'
        )
    except ImportError:
        raise ValueError(
            'Namespace "{}" 不存在'.format(namespace)
        )
    return router


def t_date(s, f='%Y-%m-%d %H:%M:%S'):
    return time.strftime(f, time.localtime(int(s)))


def lazy_import(service_name):
    """
    物流服务懒加载
    :param service_name: 服务名称
    :return: 服务类对象
    """
    try:
        namespace_ = convert_upper_case_to_snake_case(service_name)
        namespace_module = import_module(f"service.v2.{namespace_}")
        class_object = getattr(namespace_module, service_name)
    except ImportError as e:
        print(e)
        raise ValueError(
            'service_name "{}" 不存在'.format(service_name)
        )
    return class_object


def creat_or_update_logistics(db, id, data):
    """
    创建或更新物流信息
    :param db:
    :param id:
    :param data:
    :return:
    """
    if id:
        data.update({'id': id})
    elif crud.logistics_find_by_barcode(db, data['tracking_number']):
        id = crud.logistics_find_by_barcode(db, data['tracking_number']).id
        data.update({'id': id})
    else:
        id = crud.logistics_create(db, data)
        data.update({'id': id})


def query_carrier_code(db, tracking_number):
    """
    查询有无此单号物流信息
    :param db:
    :param tracking_number: 物流单号
    :return: 物流公司代码，物流单号
    """
    rs = crud.logistics_find_by_id(db, tracking_number)
    if rs:
        carrier_code = rs.carrier_code
        tracking_number = rs.tracking_number
        return carrier_code, tracking_number
    else:
        return '', ''


def time_transition(t, tz=None):
    if not tz:
        tz = pytz.timezone('Asia/Shanghai')
    return datetime.datetime.fromtimestamp(t, tz).strftime("%Y-%m-%d %H:%M:%S")
