import json

import requests

from . import app


AUTH_HEADER = f'Bearer {app.config["DROPBOX_TOKEN"]}'
UPLOAD_LINK = 'https://content.dropboxapi.com/2/files/upload'
SHARING_LINK = ('https://api.dropboxapi.com/2/'
                'sharing/create_shared_link_with_settings')

def upload_files_to_dropbox(images):
    urls = []
    if images is not None:
        for image in images:
            dropbox_args = json.dumps({
                'autorename': True,
                'path': f'/{image.filename}',
            }) 
            response = requests.post(
                UPLOAD_LINK,
                headers={
                    'Authorization': AUTH_HEADER,
                    'Content-Type': 'application/octet-stream',
                    'Dropbox-API-Arg': dropbox_args
                },
                data=image.read()
            )
            path = response.json()['path_lower']
            response = requests.post(
                SHARING_LINK,
                headers={
                    'Authorization': AUTH_HEADER,
                    'Content-Type': 'application/json',
                },
                json={'path': path}
            )
            data = response.json()
            # Проверить, есть ли ключ url на верхнем уровне ответа.
            if 'url' not in data:
                # Обходной манёвр на случай, 
                # если пользователь попытается отправить
                # один и тот же файл дважды. Ему вернётся
                # ссылка на уже существующий файл.
                data = data['error']['shared_link_already_exists']['metadata']
            # Получить ссылку по ключу.
            url = data['url']
            # Заменить режим работы ссылки, 
            # чтобы получить ссылку на скачивание.
            url = url.replace('&dl=0', '&raw=1')
            # Добавить ссылку в общий список ссылок.
            urls.append(url)
    return urls 