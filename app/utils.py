# coding: utf-8

import string
import random
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from app import application, config
from app.models import Account


def name_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def send_message(user_id, message):
    application.bot.send_text_message(user_id, message)


def encrypt(info):
    serializer = URLSafeTimedSerializer(config.SECRET_KEY)
    return serializer.dumps(info)


def decrypt(encrypted):
    serializer = URLSafeTimedSerializer(config.SECRET_KEY)
    info = serializer.loads(encrypted, max_age=config.ENCRYPTED_INFO_MAX_AGE)
    return info


def account_to_encrypted_info(account):
    info = {'account_id': account.id}
    return encrypt(info)


def encrypted_info_to_account(encrypted):
    info = decrypt(encrypted)
    return Account.query.get(info['account_id'])

