# coding: utf-8

from app import application
from app.models import Image

celery = application.celery


@celery.task()
def upload_to_imgur(image_id):
    from app.bot import send_success_upload_message

    image = Image.query.get(image_id)
    if not image:
        return

    url = 'https://api.imgur.com/3/image'
    data = {
        'image': image.facebook_url,
        'type': 'url',
        'description': " ".join(["#" + tag.text for tag in image.tags])
    }
    response_data = application.imgur.post(
        url=application.imgur.post_image_url,
        token=image.account.imgur_token,
        data=data
    )

    if response_data == None:
        token = application.imgur.refresh_token(refresh_token=image.account.imgur_refresh_token)

        image.account.imgur_token = token
        image.account.save()

        response_data = application.imgur.post(
            url=application.imgur.post_image_url,
            token=image.account.imgur_token,
            data=data
        )

    image.imgur_url = response_data['data']['link']
    image.imgur_id = response_data['data']['id']
    image.save()

    send_success_upload_message(image)




