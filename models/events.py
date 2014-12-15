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
    Field('post_approved', 'boolean', default = False),
    Field('minimum_age', 'integer', default = 0, requires = IS_NOT_EMPTY()),
    Field('fees', 'double', default = 0.0, requires = IS_NOT_EMPTY()),
    Field('expected_size', 'integer', default = 0, requires = IS_NOT_EMPTY()),
    Field('time_of_event', 'time', default = None, requires = IS_NOT_EMPTY()),
    Field('location_of_event', 'string', default = None, requires = IS_NOT_EMPTY()),
    Field('date_of_event', 'date', requires = IS_NOT_EMPTY()),
    format = '%(title)s',
    singular = 'post',
    plural = 'posts')


db.define_table('comment',
    Field('author', default = get_author(), writable = False),
    Field('email', default = get_email(), writable = False),
    Field('post_id', 'reference post', ondelete = 'NO ACTION'),
    Field('sub_comment_id', 'string'),
    Field('creation_date', 'datetime', default = datetime.utcnow(), writable = False),
    Field('modified_date', 'datetime', default = None, writable = False),
    Field('comment_content', 'text', ondelete = 'NO ACTION'),
    Field('comment_approved', 'boolean', default = False),
    singular = 'comment',
    plural = 'comments')


# This db is to keep track of who are the moderators to be able to
# view the moderator page.
db.define_table('moderator',
    Field('name', default=get_author(), writable = False, requires = IS_NOT_EMPTY()),
    Field('email', default=get_email(), writable = False, requires = IS_NOT_EMPTY(), unique = True),
    Field('moderator_status', 'boolean', default = True),
    format = '%(name)s',
    singular = 'moderator',
    plural = 'moderators')
