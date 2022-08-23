from flask_mail import Message
from flask import url_for, current_app
from flaskapp import mail
from flask_login import current_user
from ..config import Config

import secrets
import os
from PIL import Image

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=Config.MAIL_USERNAME,
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def save_picture(form_picture):
    '''
    Saves new photo to db and resize photo.It also deletes older phgoto from directory
    Returns: the name of the new photo as a string
    '''
    oldImage = current_user.image_file
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    '''
    delete old profile photo from directory 
    '''
    if oldImage != 'default.jpg':
        OldPicturePath = os.path.join(current_app.root_path, 'static/profile_pics', oldImage)
        os.system("rm -rf "+ OldPicturePath)

    return picture_fn