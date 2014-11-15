# -*- coding: utf-8 -*-
from datetime import datetime


def get_email():
    if auth.user:
        return auth.user.email
    else:
        return 'None'


def get_author():
    if auth.user:
        return '%(first_name)s %(last_name)s' % auth.user
    else:
        return 'Anonymous'


db = DAL("sqlite://storage.sqlite")


db.define_table('post',
   Field('title', 'string', requires = IS_NOT_EMPTY(), length = 50, unique = True),
   Field('author', default = get_author(), writable = False),
   Field('email', default = get_email(), writable = False),
   Field('phone', 'integer'),
   Field('creation_date', 'datetime', default = datetime.utcnow(), writable = False),
   Field('modified_date', 'datetime', default = None, writable = False),
   Field('post_content', 'text', requires = IS_NOT_EMPTY()),
   format = '%(title)s',
   singular = 'post',
   plural = 'posts')


db.define_table('comment',
   Field('author', default = get_author(), writable = False),
   Field('email', default = get_email(), writable = False),
   Field('post_id', 'reference post', ondelete = 'NO ACTION'),
   Field('creation_date', 'datetime', default = datetime.utcnow(), writable = False),
   Field('modified_date', 'datetime', default = None, writable = False),
   Field('comment_content', 'text', ondelete = 'NO ACTION'),
   singular = 'comment',
   plural = 'comments')
