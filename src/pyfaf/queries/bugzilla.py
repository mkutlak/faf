def get_bz_bug(db, bug_id):
    """
    Return BzBug instance if there is a bug in the database
    with `bug_id` id.
    """

    return (db.session.query(st.BzBug)
            .filter(st.BzBug.id == bug_id)
            .first())


def get_bz_comment(db, comment_id):
    """
    Return BzComment instance if there is a comment in the database
    with `comment_id` id.
    """

    return (db.session.query(st.BzComment)
            .filter(st.BzComment.id == comment_id)
            .first())


def get_bz_user(db, user_email):
    """
    Return BzUser instance if there is a user in the database
    with `user_id` id.
    """

    return (db.session.query(st.BzUser)
            .filter(st.BzUser.email == user_email)
            .first())


def get_bz_attachment(db, attachment_id):
    """
    Return BzAttachment instance if there is an attachment in
    the database with `attachment_id` id.
    """

    return (db.session.query(st.BzAttachment)
            .filter(st.BzAttachment.id == attachment_id)
            .first())


def get_bugzillas_by_uid(db, user_id):
    """
    Return query for BzBug for given user_id.
    """
    return db.session.query(st.BzBug).filter(st.BzBug.creator_id == user_id)

def get_bzattachments_by_uid(db, user_id):
    """
    Return query for BzAttachment objects for given user_id.
    """
    return db.session.query(st.BzAttachment).filter(st.BzAttachment.user_id == user_id)

def get_bzbugccs_by_uid(db, user_id):
    """
    Return query for BzBugCc objects for given user_id.
    """
    return db.session.query(st.BzBugCc).filter(st.BzBugCc.user_id == user_id)

def get_bzbughistory_by_uid(db, user_id):
    """
    Return query for BzBugHistory objects for given user_id.
    """
    return db.session.query(st.BzBugHistory).filter(st.BzBugHistory.user_id == user_id)

def get_bzcomments_by_uid(db, user_id):
    """
    Return query for BzComment objects for given user_id.
    """
    return db.session.query(st.BzComment).filter(st.BzComment.user_id == user_id)

def delete_bz_user(db, user_mail):
    """
    Delete BzUser instance if there is a user in the database with `user_mail` mail.
    """
    db.session.query(st.BzUser).filter(st.BzUser.email == user_mail).delete(False)


def delete_bugzilla(db, bug_id):
    """
    Delete Bugzilla for given bug_id.
    """
    query = (db.session.query(st.BzBug)
             .filter(st.BzBug.duplicate == bug_id)
             .all())

    for bgz in query:
        bgz.duplicate = None

    db.session.query(st.BzComment).filter(st.BzComment.bug_id == bug_id).delete(False)
    db.session.query(st.BzBugCc).filter(st.BzBugCc.bug_id == bug_id).delete(False)
    db.session.query(st.BzBugHistory).filter(st.BzBugHistory.bug_id == bug_id).delete(False)
    db.session.query(st.BzAttachment).filter(st.BzAttachment.bug_id == bug_id).delete(False)
    db.session.query(st.ReportBz).filter(st.ReportBz.bzbug_id == bug_id).delete(False)
    db.session.query(st.BzBug).filter(st.BzBug.id == bug_id).delete(False)
