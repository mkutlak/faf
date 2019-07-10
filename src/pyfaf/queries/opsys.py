def get_component_by_name(db, component_name, opsys_name):
    """
    Return pyfaf.storage.OpSysComponent from component name
    and operating system name or None if not found.
    """

    return (db.session.query(st.OpSysComponent)
            .join(st.OpSys)
            .filter(st.OpSysComponent.name == component_name)
            .filter(st.OpSys.name == opsys_name)
            .first())


def get_component_by_name_release(db, opsysrelease, component_name):
    """
    Return OpSysReleaseComponent instance matching `component_name`
    which also belongs to OpSysRelase instance passed as `opsysrelease`.
    """

    component = (
        db.session.query(st.OpSysReleaseComponent)
        .join(st.OpSysComponent)
        .filter(st.OpSysReleaseComponent.release == opsysrelease)
        .filter(st.OpSysComponent.name == component_name)
        .first())

    return component


def get_components_by_opsys(db, db_opsys):
    """
    Return a list of pyfaf.storage.OpSysComponent objects
    for a given pyfaf.storage.OpSys.
    """

    return (db.session.query(st.OpSysComponent)
            .filter(st.OpSysComponent.opsys == db_opsys))


def get_opsys_by_name(db, name):
    """
    Return pyfaf.storage.OpSys from operating system
    name or None if not found.
    """

    return (db.session.query(st.OpSys)
            .filter(st.OpSys.name == name)
            .first())


def get_osrelease(db, name, version):
    """
    Return pyfaf.storage.OpSysRelease from operating system
    name and version or None if not found.
    """

    return (db.session.query(st.OpSysRelease)
            .join(st.OpSys)
            .filter(st.OpSys.name == name)
            .filter(st.OpSysRelease.version == version)
            .first())


def get_releases(db, opsys_name=None, opsys_version=None):
    """
    Return query of `OpSysRelease` records optionally filtered
    by `opsys_name` and `opsys_version`.
    """

    opsysquery = (
        db.session.query(st.OpSysRelease)
        .join(st.OpSys))

    if opsys_name:
        opsysquery = opsysquery.filter(st.OpSys.name == opsys_name)

    if opsys_version:
        opsysquery = opsysquery.filter(st.OpSysRelease.version == opsys_version)

    return opsysquery


def get_supported_components(db):
    """
    Return a list of pyfaf.storage.OpSysReleaseComponent that
    are mapped to an active release (not end-of-life).
    """

    return (db.session.query(st.OpSysReleaseComponent)
            .join(st.OpSysRelease)
            .filter(st.OpSysRelease.status != 'EOL')
            .all())


def get_report_opsysrelease(db, report_id):
    return (db.session.query(st.OpSysRelease)
            .join(st.ReportOpSysRelease)
            .filter(st.ReportOpSysRelease.report_id == report_id)
            .first())


