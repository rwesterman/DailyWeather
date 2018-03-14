import json
import logging
import os

import requests


def upload_image(filename):
    """
    Uploads local image file to GroupMe hosting service, returns new file URL
    :param filename: local filename of image that is being uploaded
    :return: return content of response. This will contain the picture URL
    """

    # Check that the file exists locally
    if not os.path.exists(filename):
        logging.warning("There is no local file here: {}".format(filename))


    GM_TOKEN = os.getenv("GM_TOKEN")
    headers = {
        'X-Access-Token': GM_TOKEN,
        'Content-Type': 'image/jpeg',
    }
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            response = requests.post('https://image.groupme.com/pictures', headers=headers, data=data)
            response.raise_for_status()
    except FileNotFoundError as e:
        logging.error("No local file was found, so no image was uploaded")

    # Delete file so there isn't a local overflow
    try:
        os.remove(filename)
    except OSError:
        pass

    logging.debug("upload_image returns: {}".format(response.content))
    return response.content


def send_message(bot_id, txt = None, img_url = None, lat =  None, long = None):
    """
    Sends a message as the specified GroupMe bot, uses reqeusts.POST to send data
    :param bot_id: specific ID code for GroupMe Bot
    :param txt: Text that you want bot to send
    :param img_url: GroupME hosted image URL
    :return:
    """
    GM_url = 'https://api.groupme.com/v3/bots/post/'

    send_data = {
        'bot_id': bot_id,
        'text': txt,
        'picture_url': img_url,
        "location" : { "lat" : lat,"lng" : long}
    }

    logging.debug("Posted data: {}".format(send_data))

    r = requests.post(GM_url, data = send_data)
    logging.info(r.status_code)
    r.raise_for_status()


def retrieve_imageurl(filepath):
    """
    Accepts a local filepath, then uploads image and returns hosted URL
    :param filepath:
    :return:
    """
    img_json = json.loads(upload_image(filepath))
    logging.debug("Image URL: {}".format(img_json['payload']['picture_url']))

    return img_json['payload']['picture_url']