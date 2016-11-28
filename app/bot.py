# coding: utf-8

from flask import url_for

from app import config
from app.celery import upload_to_imgur
from app.models import Tag, Account, Image
from app.utils import account_to_encrypted_info, send_message


def send_success_login_message(account):
    send_message(account.fb_messenger_id, BOT_MESSAGES['success_login'].format(
        account.imgur_username
    ))


def send_success_upload_message(image):
    send_message(image.account.fb_messenger_id, BOT_MESSAGES['uploaded'].format(
        image.imgur_url
    ))


def process_facebook_data(data):
    entries = data.get('entry')
    if not entries:
        return

    for entry in entries:
        messages = entry.get('messaging')
        if not messages:
            continue
        for message in messages:
            user_id = message['sender']['id']

            account, created = Account.get_or_create(user_id)
            if created:
                send_message(user_id, BOT_MESSAGES['hello'])
                send_message(user_id, BOT_MESSAGES['help'])
                return

            text = message['message'].get('text')
            attachments = message['message'].get('attachments')
            if not text:
                continue

            splitted = text.split()
            command = splitted[0]
            command_info = COMMANDS.get(command)
            if not command_info:
                send_message(user_id, BOT_MESSAGES['no_command'].format(command))
                send_message(user_id, BOT_MESSAGES['help'])
                continue
            command_info[1](account, text, attachments)


def process_help(account, text, attachmets):
    send_message(account.fb_messenger_id, BOT_MESSAGES['help'])


def process_info(account, text, attachments):
    if not account.is_loggined_to_imgur():
        send_message(account.fb_messenger_id, BOT_MESSAGES['info_not_authorized'])
    else:
        send_message(account.fb_messenger_id, BOT_MESSAGES['info'].format(account.imgur_username))


def process_authorize(account, text, attachments):
    encrypted = account_to_encrypted_info(account)
    url = '{}{}?info={}'.format(
        config.URL,
        url_for('login'),
        encrypted
    )
    send_message(account.fb_messenger_id, BOT_MESSAGES['login'])
    send_message(account.fb_messenger_id, url)


def process_post(account, text, attachmets):
    if not account.is_loggined_to_imgur():
        send_message(account.fb_messenger_id, BOT_MESSAGES['not_authorized'])
        return

    if not attachmets:
        send_message(account.fb_messenger_id, BOT_MESSAGES['no_attachments'])
        return

    tags = list(filter(lambda x: x.startswith('#'), text.split()))
    tags = [tag.replace('#', '') for tag in tags]

    tags_objects = Tag.from_str_list(tags)
    images = list(filter(lambda x: x.get('type') == 'image', attachmets))

    for im in images:
        image = Image()
        image.facebook_url = im['payload']['url']
        image.account_id = account.id
        for tag in tags_objects:
            image.tags.append(tag)
        image.save()

        send_message(account.fb_messenger_id, BOT_MESSAGES['start_upload'])
        upload_to_imgur.delay(image.id)

COMMANDS = {
    '/help': ['show help message(this)', process_help],
    '/authorize': ['return authorization link', process_authorize],
    '/post': ['upload message and tags to your Imgur account', process_post],
    '/info': ['show user info', process_info],
}


BOT_MESSAGES = {
    'start_upload': "Ok, got your picture, let's upload it!",
    'info': 'You give me access to {} Imgur account',
    'info_not_authorized': "You don't give me access at your Imgur account. Call /authorize to give me access",
    'not_authorized': 'Before upload picture, please authorize me at Imgur. Call /authorize to give me access"',
    'success_login': "I'am successfully authorized at your Imgur account {}",
    'uploaded': 'Successfully upload image to Imgur\nLink: {}',
    'no_command': 'Sorry. Cannot find command {}',
    'no_attachments': 'Sorry, there is no attached images at message',
    'login': 'Here is the authorization link. Click on it to allow me upload pictures (will be valid 12 hours):',
    'hello': """
Hello! My name is Picture-Bot and I'am a bot)
My goal is to help you upload images on Imgur.
First of all you need to give me access to your acount( /authorize command)
    """,
    'help': """
This is my available commands:

{}
    """.format("\n".join(["{}: {}".format(command_name, info[0]) for command_name, info in COMMANDS.items()]))
}
