def get_user_by_mail(db, mail):
    """
    Return query for User objects for given mail.
    """
    return db.session.query(st.User).filter(st.User.mail == mail)
