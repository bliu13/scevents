# -*- coding: utf-8 -*-

#########################################################################
## This is the controller for scevents
#########################################################################

def index():
    """
    This function is responsible for retrieving the table of posts and
    is also called by default/index.html to display the appropriate
    contents of the notes table to the user.
    """

    # Grabs all the rows in the database.
    posts = db(db.post).select()
    comments = db(db.comment).select()

    if auth.user_id is None:
        # If the user id is None, then the user is not logged in.
        response.flash = T("You must log in to manage your posts.")

    return dict(posts=posts, comments=comments)


@auth.requires_login()
def add():
    """
    Adds a record to post db.
    """
    form = SQLFORM(db.post)
    if form.process().accepted:
        # The form content was valid and is accepted
        session.flash = T("Added the new post successfully.")
        redirect(URL('default', 'index'))

    return dict(form=form)


@auth.requires_login()
def edit():
    """
    Edits a record from post db.
    """

    # Grabs the post id for what the user requested.
    post = db.post(request.args(0))

    # Checks to see if the post exists.
    if post is None:
        session.flash = T("Invalid Request: Post does not exist.")
        redirect(URL('default', 'index'))

    # Checks to see if the current user was the author of post.
    if post.email != auth.user.email:
        session.flash = T("Invalid Request: Not the author of the post.")
        redirect(URL('default', 'index'))

    # Begins editing of the note here.
    form = SQLFORM(db.post, record=post)
    if form.process().accepted:
        # Shows that edit is done after redirecting to the index.
        session.flash = T("Edit is done.")
        redirect(URL('default', 'index'))

    # Updates the modified_date in database with the same id as the one in this post.
    db(db.post.id == post.id).update(modified_date = datetime.utcnow())

    return dict(form=form)


def post():
    """
    Reads a record from post db. Also serves the comments for this post.

    Bug: post_content is not displayed correctly. If users create linebreaks
         in their post, it will not show at all on the view side because
         'linebreak' is supposed to start a new paragraph. Current implementation
         stuffs all the post_content under one paragraph. Possible solution is
         to implement support for multiple <p> creation on the view side or shove
         the post_content into <textarea> and make <textarea> borderless.
    """

    # Grabs the post id for what the user requested.
    post = db.post(request.args(0))

    # Checks to see if the post exists.
    if post is None:
        session.flash = T("Invalid Request: Post does not exist.")
        redirect(URL('default', 'index'))

    comments = db(db.comment.post_id==request.args(0)).select()
    post_url_comment = URL('add_user_comment')
    post_url_editpost = URL('edit_user_post')
    post_url_editcomment = URL('edit_user_post')

    return dict(post=post, comments=comments, post_url_comment=post_url_comment,\
                post_url_editpost=post_url_editpost, post_url_editcomment=post_url_editcomment)


@auth.requires_login()
def add_user_comment():
    """
    This function should not be 'viewed' directly and is used for AJAX processing
    of data. This function's job is to take user comments and commit them into the
    database.

    Bug: comment_content is not displayed correctly. If users create linebreaks
         in their comment, it will not show at all on the view side because
         'linebreak' is supposed to start a new paragraph. Current implementation
         stuffs all the comment_content under one paragraph. Possible solution is
         to implement support for multiple <p> creation on the view side or shove
         the comment_content into <textarea> and make <textarea> borderless.
    """
    comment_data = request.vars.comment_data or ''

    # Here is the bullshit, what is sent from the client side is in a form of a string
    # and no matter what kind of data structure you created on the other side, it won't
    # matter here so you must recreate the data yourself.
    #
    # What is being done here is we are separating the data that is supposed to be post_id.
    post_id = ""
    comment_string = ""
    for index in range(len(comment_data)):
        if comment_data[index] is not ',':
            # The first comma in the info passed in was the comma for separating
            # the array data.
            post_id = post_id + comment_data[index]
        else:
            # The rest of the string is the user's comment.
            comment_string = comment_data[(index+1):]
            # Convert post_id from str to int
            post_id = int(post_id)
            break

    latest_comment = db.comment.insert(post_id=post_id, comment_content=comment_string)

    # Grab the latest comment entry
    latest_comment_entry = db.comment(latest_comment)
    comment_author = latest_comment_entry.author
    comment_creation_date = latest_comment_entry.creation_date
    comment_modified_date = latest_comment_entry.modified_date
    comment_content = latest_comment_entry.comment_content

    return response.json(dict(comment_author=comment_author, comment_creation_date=comment_creation_date,\
                              comment_modified_date=comment_modified_date, comment_content=comment_content))


@auth.requires_login()
def edit_user_post():
    """
    This function should not be 'viewed' directly and is used for AJAX processing
    of data. This function's job is to take user's edited post and commit them into the
    database.

    Bug: post_content is not displayed correctly. If users create linebreaks
         in their post, it will not show at all on the view side because
         'linebreak' is supposed to start a new paragraph. Current implementation
         stuffs all the post_content under one paragraph. Possible solution is
         to implement support for multiple <p> creation on the view side or shove
         the post_content into <textarea> and make <textarea> borderless.
    """
    post_data = request.vars.post_data or ''

    # Here is the bullshit, what is sent from the client side is in a form of a string
    # and no matter what kind of data structure you created on the other side, it won't
    # matter here so you must recreate the data yourself.
    #
    # What is being done here is we are separating the data that is supposed to be post_id.
    post_id = ""
    post_string = ""
    for index in range(len(post_data)):
        if post_data[index] is not ',':
            # The first comma in the info passed in was the comma for separating
            # the array data.
            post_id = post_id + post_data[index]
        else:
            # The rest of the string is the user's comment.
            post_string = post_data[(index+1):]
            # Convert post_id from str to int
            post_id = int(post_id)
            break

    db(db.post.id == post_id).update(post_content=post_string, modified_date=datetime.utcnow())

    # Grab the latest comment entry
    updated_post_entry = db.post(post_id)
    post_author = updated_post_entry.author
    post_creation_date = updated_post_entry.creation_date
    post_modified_date = updated_post_entry.modified_date
    post_content = updated_post_entry.post_content

    return response.json(dict(post_author=post_author, post_creation_date=post_creation_date,\
                              post_modified_date=post_modified_date, post_content=post_content))


@auth.requires_login()
def add_comment():
    """
    This function along with default/add_comment.html is temporary and
    is only used for initial testing purposes.

    Adds a record to comment db.
    """
    form = SQLFORM(db.comment)
    if form.process().accepted:
        # The form content was valid and is accepted
        session.flash = T("Added the new post successfully.")
        redirect(URL('default', 'index'))

    return dict(form=form)


@auth.requires_login()
def edit_comment():
    """
    This function along with default/edit_comment.html is temporary and
    is only used for initial testing purposes.

    Edits a record from post db.
    """

    # Grabs the post id for what the user requested.
    comment = db.comment(request.args(0))

    # Checks to see if the post exists.
    if comment is None:
        session.flash = T("Invalid Request: Post does not exist.")
        redirect(URL('default', 'index'))

    # Checks to see if the current user was the author of post.
    if comment.email != auth.user.email:
        session.flash = T("Invalid Request: Not the author of the post.")
        redirect(URL('default', 'index'))

    # Begins editing of the note here.
    form = SQLFORM(db.comment, record=comment)
    if form.process().accepted:
        # Shows that edit is done after redirecting to the index.
        session.flash = T("Edit is done.")
        redirect(URL('default', 'index'))

    # Updates the modified_date in database with the same id as the one in this post.
    db(db.comment.id == comment.id).update(modified_date = datetime.utcnow())

    return dict(form=form)


def read_comment():
    """
    This function along with default/read_comment.html is temporary and
    is only used for initial testing purposes.

    Reads a record from comment db.
    """

    # Grabs the post id for what the user requested.
    comment = db.comment(request.args(0))

    # Checks to see if the post exists.
    if comment is None:
        session.flash = T("Invalid Request: Post does not exist.")
        redirect(URL('default', 'index'))

    # Form is created to be viewed and is made to be read only
    form = SQLFORM(db.comment, record=comment, readonly=True)
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login()
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
