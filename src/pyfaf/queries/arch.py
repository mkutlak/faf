
def get_arch_by_name(db, arch_name):
    """
    Return pyfaf.storage.Arch object from architecture
    name or None if not found.
    """

    return (db.session.query(st.Arch)
            .filter(st.Arch.name == arch_name)
            .first())


def get_archs(db):
    """
    Returns the list of all pyfaf.storage.Arch objects.
    """

    return (db.session.query(st.Arch)
            .all())


