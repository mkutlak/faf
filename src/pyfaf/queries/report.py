def get_backtrace_by_hash(db, bthash):
    """
    Return pyfaf.storage.ReportBacktrace object from ReportBtHash.hash
    or None if not found.
    """

    return (db.session.query(st.ReportBacktrace)
            .join(st.ReportBtHash)
            .filter(st.ReportBtHash.hash == bthash)
            .first())


def get_backtraces_by_type(db, reporttype, query_all=True):
    """
    Return a list of pyfaf.storage.ReportBacktrace objects
    from textual report type.
    """

    query = (db.session.query(st.ReportBacktrace)
             .join(st.Report)
             .filter(st.Report.type == reporttype))

    if not query_all:
        query = query.filter((st.ReportBacktrace.crashfn.is_(None)) |
                             (st.ReportBacktrace.crashfn == "??"))

    return query


def get_history_day(db, db_report, db_osrelease, day):
    """
    Return pyfaf.storage.ReportHistoryDaily object for a given
    report, opsys release and day or None if not found.
    """
    if not db_report.id:
        return None

    return (db.session.query(st.ReportHistoryDaily)
            .filter(st.ReportHistoryDaily.report == db_report)
            .filter(st.ReportHistoryDaily.opsysrelease == db_osrelease)
            .filter(st.ReportHistoryDaily.day == day)
            .first())


def get_history_month(db, db_report, db_osrelease, month):
    """
    Return pyfaf.storage.ReportHistoryMonthly object for a given
    report, opsys release and month or None if not found.
    """
    if not db_report.id:
        return None

    return (db.session.query(st.ReportHistoryMonthly)
            .filter(st.ReportHistoryMonthly.report == db_report)
            .filter(st.ReportHistoryMonthly.opsysrelease == db_osrelease)
            .filter(st.ReportHistoryMonthly.month == month)
            .first())


def get_history_sum(db, opsys_name=None, opsys_version=None,
                    history='daily'):
    """
    Return query summing ReportHistory(Daily|Weekly|Monthly)
    records optinaly filtered by `opsys_name` and `opsys_version`.
    """

    opsysrelease_ids = get_release_ids(db, opsys_name, opsys_version)
    hist_table, _ = get_history_target(history)
    hist_sum = db.session.query(func.sum(hist_table.count).label('cnt'))
    if opsysrelease_ids:
        hist_sum = hist_sum.filter(
            hist_table.opsysrelease_id.in_(opsysrelease_ids))

    return hist_sum


def get_history_target(target='daily'):
    """
    Return tuple of `ReportHistory(Daily|Weekly|Monthly)` and
    proper date field `ReportHistory(Daily.day|Weekly.week|Monthly.month)`
    according to `target` parameter which should be one of
    `daily|weekly|monthly` or shortened version `d|w|m`.
    """

    if target in ['d', 'daily']:
        return (st.ReportHistoryDaily, st.ReportHistoryDaily.day)

    if target in ['w', 'weekly']:
        return (st.ReportHistoryWeekly, st.ReportHistoryWeekly.week)

    return (st.ReportHistoryMonthly, st.ReportHistoryMonthly.month)


def get_history_week(db, db_report, db_osrelease, week):
    """
    Return pyfaf.storage.ReportHistoryWeekly object for a given
    report, opsys release and week or None if not found.
    """
    if not db_report.id:
        return None

    return (db.session.query(st.ReportHistoryWeekly)
            .filter(st.ReportHistoryWeekly.report == db_report)
            .filter(st.ReportHistoryWeekly.opsysrelease == db_osrelease)
            .filter(st.ReportHistoryWeekly.week == week)
            .first())


def get_report_by_id(db, report_id):
    """
    Return pyfaf.storage.Report object by report_id
    or None if not found.
    """

    return (db.session.query(st.Report)
            .filter(st.Report.id == report_id)
            .first())


def get_report(db, report_hash, os_name=None, os_version=None, os_arch=None):
    '''
    Return pyfaf.storage.Report object or None if not found
    This method takes optionally parameters for searching
    Reports by os parameters
    '''

    db_query = (db.session.query(st.Report)
                .join(st.ReportHash)
                .filter(st.ReportHash.hash == report_hash))

    if os_name:
        osplugin = systems[os_name]

        db_query = (db_query
                    .join(st.ReportOpSysRelease)
                    .join(st.OpSysRelease, st.ReportOpSysRelease.opsysrelease_id == st.OpSysRelease.id)
                    .join(st.OpSys, st.OpSysRelease.opsys_id == st.OpSys.id)
                    .filter(st.OpSys.name == osplugin.nice_name)
                    .filter(st.ReportOpSysRelease.report_id == st.Report.id))

    if os_version:
        if not os_name:
            db_query = (db_query.join(st.ReportOpSysRelease))

        db_query = (db_query
                    .filter(st.OpSysRelease.version == os_version))

    if os_arch:
        db_query = (db_query
                    .join(st.ReportArch)
                    .join(st.Arch, st.ReportArch.arch_id == st.Arch.id)
                    .filter(st.Arch.name == os_arch))

    return db_query.first()


def get_report_count_by_component(db, opsys_name=None, opsys_version=None,
                                  history='daily'):
    """
    Return query for `OpSysComponent` and number of reports this
    component received.

    Optionally filtered by `opsys_name` and `opsys_version`.
    """

    opsysrelease_ids = get_release_ids(db, opsys_name, opsys_version)
    hist_table, _ = get_history_target(history)

    comps = (
        db.session.query(st.OpSysComponent,
                         func.sum(hist_table.count).label('cnt'))
        .join(st.Report, st.Report.component_id == st.OpSysComponent.id)
        .join(hist_table)
        .group_by(st.OpSysComponent)
        .order_by(desc('cnt')))

    if opsysrelease_ids:
        comps = comps.filter(hist_table.opsysrelease_id.in_(opsysrelease_ids))

    return comps


def get_report_release_desktop(db, db_report, db_release, desktop):
    """
    Return `pyfaf.storage.ReportReleaseDesktop` object for given
    report, release and desktop or None if not found.
    """
    if not db_report.id:
        return None

    return (db.session.query(st.ReportReleaseDesktop)
            .filter(st.ReportReleaseDesktop.report == db_report)
            .filter(st.ReportReleaseDesktop.release == db_release)
            .filter(st.ReportReleaseDesktop.desktop == desktop)
            .first())


def get_report_stats_by_component(db, component, opsys_name=None,
                                  opsys_version=None, history='daily'):
    """
    Return query with reports for `component` along with
    summed counts from `history` table (one of daily/weekly/monthly).

    Optionally filtered by `opsys_name` and `opsys_version`.
    """

    hist_table, _ = get_history_target(history)
    opsysrelease_ids = get_release_ids(db, opsys_name, opsys_version)

    stats = (db.session.query(st.Report,
                              func.sum(hist_table.count).label('cnt'))
             .join(hist_table, hist_table.report_id == st.Report.id)
             .join(st.OpSysComponent)
             .filter(st.OpSysComponent.id == component.id)
             .group_by(st.Report)
             .order_by(desc('cnt')))

    if opsysrelease_ids:
        stats = stats.filter(hist_table.opsysrelease_id.in_(opsysrelease_ids))

    return stats


def get_reportarch(db, report, arch):
    """
    Return pyfaf.storage.ReportArch object from pyfaf.storage.Report
    and pyfaf.storage.Arch or None if not found.
    """
    if not report.id:
        return None

    return (db.session.query(st.ReportArch)
            .filter(st.ReportArch.report == report)
            .filter(st.ReportArch.arch == arch)
            .first())


def get_reportexe(db, report, executable):
    """
    Return pyfaf.storage.ReportExecutable object from pyfaf.storage.Report
    and the absolute path of executable or None if not found.
    """
    if not report.id:
        return None

    return (db.session.query(st.ReportExecutable)
            .filter(st.ReportExecutable.report == report)
            .filter(st.ReportExecutable.path == executable)
            .first())


def get_reportosrelease(db, report, osrelease):
    """
    Return pyfaf.storage.ReportOpSysRelease object from pyfaf.storage.Report
    and pyfaf.storage.OpSysRelease or None if not found.
    """
    if not report.id:
        return None

    return (db.session.query(st.ReportOpSysRelease)
            .filter(st.ReportOpSysRelease.report == report)
            .filter(st.ReportOpSysRelease.opsysrelease == osrelease)
            .first())


def get_reportpackage(db, report, package):
    """
    Return pyfaf.storage.ReportPackage object from pyfaf.storage.Report
    and pyfaf.storage.Package or None if not found.
    """
    if not report.id:
        return None

    return (db.session.query(st.ReportPackage)
            .filter(st.ReportPackage.report == report)
            .filter(st.ReportPackage.installed_package == package)
            .first())


def get_reportreason(db, report, reason):
    """
    Return pyfaf.storage.ReportReason object from pyfaf.storage.Report
    and the textual reason or None if not found.
    """
    if not report.id:
        return None

    return (db.session.query(st.ReportReason)
            .filter(st.ReportReason.report == report)
            .filter(st.ReportReason.reason == reason)
            .first())


def get_reports_by_type(db, report_type, min_count=0):
    """
    Return pyfaf.storage.Report object list from
    the textual type or an empty list if not found.
    """
    q = (db.session.query(st.Report)
         .filter(st.Report.type == report_type))
    if min_count > 0:
        q = q.filter(st.Report.count >= min_count)
    return q.all()

def get_reports_for_problems(db, report_type):
    """
    Return pyfaf.storage.Report objects list.
    For each problem get only one report.
    """
    query = (db.session.query(st.Report.problem_id.label('p_id'),
                              func.min(st.Report.id).label('min_id'))
             .filter(st.Report.type == report_type))

    query = query.filter(st.Report.problem_id.isnot(None))

    query = (query.group_by(st.Report.problem_id).subquery())

    final_query = (db.session.query(st.Report)
                   .filter(query.c.min_id == st.Report.id))
    return final_query.all()

def get_unassigned_reports(db, report_type, min_count=0):
    """
    Return pyfaf.storage.Report objects list of reports without problems.
    """
    query = (db.session.query(st.Report)
             .filter(st.Report.type == report_type)
             .filter(st.Report.problem_id.is_(None)))
    if min_count > 0:
        query = query.filter(st.Report.count >= min_count)
    return query.all()

def remove_problem_from_low_count_reports_by_type(db, report_type, min_count):
    """
    Set problem_id = NULL for reports of given `report_type` where count is
    less than `min_count`.
    """

    return (db.session.query(st.Report)
            .filter(st.Report.type == report_type)
            .filter(st.Report.count < min_count)
            .update({st.Report.problem_id: None},
                    synchronize_session=False))


def get_reportbz(db, report_id, opsysrelease_id=None):
    """
    Return pyfaf.storage.ReportBz objects of given `report_id`.
    Optionally filter by `opsysrelease_id` of the BzBug.
    """

    query = (db.session.query(st.ReportBz)
             .filter(st.ReportBz.report_id == report_id))
    if opsysrelease_id:
        query = (query.join(st.BzBug)
                 .filter(st.BzBug.opsysrelease_id == opsysrelease_id))

    return query


def get_reportbz_by_major_version(db, report_id, major_version):
    """
    Return pyfaf.storage.ReportBz objects of given `report_id`.
    Optionally filter by `opsysrelease_id` of the BzBug.
    """

    query = (db.session.query(st.ReportBz)
             .join(st.BzBug)
             .join(st.OpSysRelease)
             .filter(st.ReportBz.report_id == report_id)
             .filter(st.OpSysRelease.version.like(str(major_version) + ".%")))

    return query


def get_reportmantis(db, report_id, opsysrelease_id=None):
    """
    Return pyfaf.storage.ReportMantis objects of given `report_id`.
    Optionally filter by `opsysrelease_id` of the MantisBug.
    """
    query = (db.session.query(st.ReportMantis)
             .filter(st.ReportMantis.report_id == report_id))
    if opsysrelease_id:
        query = (query.join(st.MantisBug)
                 .filter(st.MantisBug.opsysrelease_id == opsysrelease_id))

    return query


def get_unknown_package(db, db_report, role, name,
                        epoch, version, release, arch):
    """
    Return pyfaf.storage.ReportUnknownPackage object from pyfaf.storage.Report,
    package role and NEVRA or None if not found.
    """
    if not db_report.id:
        return None

    db_arch = get_arch_by_name(db, arch)
    return (db.session.query(st.ReportUnknownPackage)
            .filter(st.ReportUnknownPackage.report == db_report)
            .filter(st.ReportUnknownPackage.type == role)
            .filter(st.ReportUnknownPackage.name == name)
            .filter(st.ReportUnknownPackage.epoch == epoch)
            .filter(st.ReportUnknownPackage.version == version)
            .filter(st.ReportUnknownPackage.release == release)
            .filter(st.ReportUnknownPackage.arch == db_arch)
            .first())


def update_frame_ssource(db, db_ssrc_from, db_ssrc_to):
    """
    Replaces pyfaf.storage.SymbolSource `db_ssrc_from` by `db_ssrc_to` in
    all affected frames.
    """

    db_frames = (db.session.query(st.ReportBtFrame)
                 .filter(st.ReportBtFrame.symbolsource == db_ssrc_from))

    for db_frame in db_frames:
        db_frame.symbolsource = db_ssrc_to

    db.session.flush()


def get_crashed_unknown_package_nevr_for_report(db, report_id):
    """
    Return (n,e,v,r) tuples for and unknown packages that CRASHED in a given
    report.
    """
    return (db.session.query(st.ReportUnknownPackage.name,
                             st.ReportUnknownPackage.epoch,
                             st.ReportUnknownPackage.version,
                             st.ReportUnknownPackage.release)
            .filter(st.ReportUnknownPackage.report_id == report_id)
            .filter(st.ReportUnknownPackage.type == "CRASHED")
            .all())


def get_reports_for_opsysrelease(db, problem_id, opsysrelease_id):
    return (db.session.query(st.Report)
            .join(st.ReportOpSysRelease)
            .filter(st.ReportOpSysRelease.opsysrelease_id == opsysrelease_id)
            .filter(st.Report.problem_id == problem_id).all())


def get_all_report_hashes(db, date_from=None,
                          date_to=None,
                          opsys=None,
                          opsys_releases=None,
                          limit_from=None,
                          limit_to=None
                         ):
    """
    Return ReportHash instance if there is at least one bug in database for selected date range
    """
    query = (db.session.query(st.ReportHash)
             .join(st.Report)
             .options(load_only("hash"))
            )

    if opsys and opsys != "*":
        if opsys == "rhel":
            opsys = "Red Hat Enterprise Linux"

        query = (query.join(st.ReportOpSysRelease)
                 .join(st.OpSysRelease)
                 .join(st.OpSys)
                 .filter(st.OpSys.name == opsys))

        if opsys_releases and opsys_releases != "*":
            query = (query.filter(st.OpSysRelease.version == opsys_releases))

    if date_from and date_from != "*":
        query = (query.filter(st.Report.last_occurrence >= date_from))

    if date_to and date_to != "*":
        query = (query.filter(st.Report.last_occurrence <= date_to))

    if limit_from is not None and limit_to is not None:
        query = (query.slice(limit_from, limit_to))

    return query.all()

def get_reportarchives_by_username(db, username):
    """
    Returns query for ReportArchive objects for given username.
    """
    return db.session.query(st.ReportArchive).filter(st.ReportArchive.username == username)


def get_report_contact_email(db, report_id, contact_email_id):
    """
    Return ReportContactEmail for a given report_id and contact_email_id
    """
    return (db.session.query(st.ReportContactEmail)
            .filter(st.ReportContactEmail.contact_email_id == contact_email_id)
            .filter(st.ReportContactEmail.report_id == report_id)
            .first())


def get_reportcontactmails_by_id(db, contact_email_id):
    """
    Return a query for ReportContactEmail objects for given contact_email_id
    """
    return (db.session.query(st.ReportContactEmail)
            .filter(st.ReportContactEmail.contact_email_id == contact_email_id))

