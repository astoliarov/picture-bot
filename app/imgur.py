# coding: utf-8

import json
import requests


class ImgurApi:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

        self.post_image_url = 'https://api.imgur.com/3/image'
        self.token_url = 'https://api.imgur.com/oauth2/token'
        self.authorize_url = 'https://api.imgur.com/oauth2/authorize'

    def get_oauth_url(self, state):
        return '{}?client_id={}&response_type=code&state={}'.format(
                self.authorize_url,
                self.client_id,
                state
            )

    def get_token_from_code(self, code):
        response = requests.post(self.token_url, data={
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code
        })

        response_data = json.loads(response.text)
        return response_data

    def refresh_token(self, refresh_token):
        data = {
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        response = requests.post(self.token_url, data=data)
        data = json.loads(response.text)
        return data['access_token']

    def post(self, url, token, data=None, headers=None):
        if headers is None:
            headers = {}

        if data is None:
            data = {}

        headers['Authorization'] = 'Bearer {}'.format(token)
        response = requests.post(
            url=url,
            data=data,
            headers=headers
        )
        if response.status_code == 403:
            return None

        response_data = json.loads(response.text)
        return response_data



