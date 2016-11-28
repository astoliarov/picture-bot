# coding: utf-8

import json
import requests
from itsdangerous import SignatureExpired, BadSignature

from flask import request, redirect, render_template
from flask.views import MethodView

from app import application, config
from app.bot import process_facebook_data, send_success_login_message
from app.utils import encrypted_info_to_account, account_to_encrypted_info


class WebhookView(MethodView):
    def get(self, *args, **kwargs):
        verify_token = request.args.get('hub.verify_token')
        if verify_token == 'mAoR81uC2dk3y8KM0EX3VUU51GKRGUUn':
            return request.args['hub.challenge'], 200
        else:
            return '', 400

    def post(self, *args, **kwargs):
        if not request.data:
            return '', 403
        data = json.loads(request.data.decode('utf-8'))
        process_facebook_data(data)
        return '', 200

application.add_url_rule('/bot/webhook',  'webhook',
        methods=['GET', 'POST'],
        view_func=WebhookView.as_view('webhook'),
        strict_slashes=False)


@application.route('/imgur/login', methods=['GET'], strict_slashes=False)
def login():
    info = request.args.get('info')
    if not info:
        return "No info", 400

    try:
        account = encrypted_info_to_account(info)
    except SignatureExpired:
        return render_template('400.html'), 400
    except BadSignature:
        return render_template('400.html'), 400

    if not account:
        return render_template('404.html'), 404

    # Regenerate encrypted info to prevent expiered error
    info = account_to_encrypted_info(account)

    url = 'https://api.imgur.com/oauth2/authorize?client_id={}&response_type=code&state={}'.format(
        config.IMGUR_CLIENT_ID,
        info
    )
    return redirect(url)


@application.route('/imgur/callback', methods=['GET'], strict_slashes=False)
def callback():
    code = request.args.get('code')
    info = request.args.get('state')
    if not code or not info:
        return render_template('400.html'), 400

    try:
        account = encrypted_info_to_account(info)
    except SignatureExpired:
        return render_template('400.html'), 400
    except BadSignature:
        return render_template('400.html'), 400

    if not account:
        return render_template('404.html'), 404


    # make request in view to process data and show user info
    response = requests.post('https://api.imgur.com/oauth2/token', data={
        'client_id': config.IMGUR_CLIENT_ID,
        'client_secret': config.IMGUR_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code
    })

    try:
        response_data = json.loads(response.text)
    except json.JSONDecodeError:
        return render_template('500.html'), 500

    # not update account model if user try to authorize the same account
    if account.imgur_account_id == response_data['account_id']:
        return render_template("authorized.html", username=account.imgur_username), 200

    account.imgur_username = response_data['account_username']
    account.imgur_token = response_data['access_token']
    account.imgur_refresh_token = response_data['refresh_token']
    account.imgur_account_id = response_data['account_id']
    account.save()
    send_success_login_message(account)

    return render_template('info.html', username=response_data['account_username']), 200


