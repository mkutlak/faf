# Copyright (C) 2013  ABRT Team
# Copyright (C) 2013  Red Hat, Inc.
#
# This file is part of faf.
#
# faf is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# faf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with faf.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import functools
from sqlalchemy import func, desc
from sqlalchemy.orm import load_only, aliased

from pyfaf.opsys import systems
import pyfaf.storage as st

__all__ = ["get_arch_by_name", "get_archs", "get_associate_by_name",
           "get_backtrace_by_hash", "get_backtraces_by_type",
           "get_bugtracker_by_name", "get_bz_attachment", "get_bz_bug",
           "get_bz_comment", "get_bz_user",
           "get_component_by_name", "get_components_by_opsys",
           "get_contact_email", "get_report_contact_email",
           "get_crashed_package_for_report",
           "get_crashed_unknown_package_nevr_for_report",
           "get_debug_files", "get_external_faf_by_baseurl",
           "get_external_faf_by_id", "get_external_faf_by_name",
           "get_external_faf_instances", "get_history_day", "get_history_month",
           "get_history_sum", "get_history_target", "get_history_week",
           "get_sf_prefilter_btpath_by_pattern", "get_sf_prefilter_btpaths",
           "get_sf_prefilter_btpaths_by_solution",
           "get_sf_prefilter_pkgname_by_pattern",
           "get_sf_prefilter_pkgnames", "get_sf_prefilter_pkgnames_by_solution",
           "get_sf_prefilter_sol", "get_sf_prefilter_sols",
           "get_sf_prefilter_sol_by_cause", "get_sf_prefilter_sol_by_id",
           "get_kernelmodule_by_name", "get_opsys_by_name", "get_osrelease",
           "get_package_by_file", "get_packages_by_file",
           "get_package_by_file_build_arch", "get_packages_by_file_builds_arch",
           "get_package_by_name_build_arch", "get_package_by_nevra",
           "get_problem_by_id", "get_problems", "get_problem_component",
           "get_empty_problems", "get_problem_opsysrelease",
           "get_build_by_nevr", "get_release_ids", "get_releases", "get_report",
           "get_report_count_by_component", "get_report_release_desktop",
           "get_report_stats_by_component", "get_report_by_id",
           "get_reports_for_problems", "get_reportarch", "get_reportexe",
           "get_reportosrelease", "get_reportpackage", "get_reportreason",
           "get_reports_by_type", "get_reportbz", "get_reportmantis",
           "get_reports_for_opsysrelease", "get_repos_for_opsys",
           "get_src_package_by_build", "get_ssource_by_bpo",
           "get_ssources_for_retrace", "get_supported_components",
           "get_symbol_by_name_path", "get_symbolsource",
           "get_taint_flag_by_ureport_name", "get_unassigned_reports",
           "get_unknown_opsys", "get_unknown_package", "update_frame_ssource",
           "query_hot_problems", "query_longterm_problems",
           "user_is_maintainer", "get_packages_by_osrelease", "get_all_report_hashes",
           "delete_bz_user", "get_reportcontactmails_by_id",
           "get_reportarchives_by_username", "get_problemreassigns_by_username",
           "get_user_by_mail", "delete_bugzilla", "get_bugzillas_by_uid",
           "get_bzattachments_by_uid", "get_bzbugccs_by_uid",
           "get_bzbughistory_by_uid", "get_bzcomments_by_uid",
           "get_bz_comment", "get_bz_user", "get_builds_by_opsysrelease_id",
           "delete_mantis_bugzilla"]


def get_associate_by_name(db, name):
    """
    Returns pyfaf.storage.AssociatePeople object with given
    `name` or None if not found.
    """

    return (db.session.query(st.AssociatePeople)
            .filter(st.AssociatePeople.name == name)
            .first())




def get_contact_email(db, email_address):
    """
    Return ContactEmail for a given email_address
    """
    return (db.session.query(st.ContactEmail)
            .filter(st.ContactEmail.email_address == email_address)
            .first())




def get_debug_files(db, db_package):
    """
    Returns a list of debuginfo files provided by `db_package`.
    """

    deps = (db.session.query(st.PackageDependency)
            .filter(st.PackageDependency.package == db_package)
            .filter(st.PackageDependency.type == "PROVIDES")
            .filter((st.PackageDependency.name.like("/%%.ko.debug") |
                     (st.PackageDependency.name.like("/%%/vmlinux"))))
            .all())

    return [dep.name for dep in deps]


def get_external_faf_by_baseurl(db, baseurl):
    """
    Return pyfaf.storage.ExternalFafInstance with the given
    `baseurl` or None if not found.
    """

    return (db.session.query(st.ExternalFafInstance)
            .filter(st.ExternalFafInstance.baseurl == baseurl)
            .first())


def get_external_faf_by_id(db, faf_instance_id):
    """
    Return pyfaf.storage.ExternalFafInstance saved under the given
    `faf_instance_id` or None if not found.
    """

    return (db.session.query(st.ExternalFafInstance)
            .filter(st.ExternalFafInstance.id == faf_instance_id)
            .first())


def get_external_faf_by_name(db, name):
    """
    Return pyfaf.storage.ExternalFafInstance with the given
    `name` or None if not found.
    """

    return (db.session.query(st.ExternalFafInstance)
            .filter(st.ExternalFafInstance.name == name)
            .first())


def get_external_faf_instances(db):
    """
    Return a list of all pyfaf.storage.ExternalFafInstance objects.
    """

    return (db.session.query(st.ExternalFafInstance)
            .all())




def get_sf_prefilter_btpath_by_pattern(db, pattern):
    """
    Return a pyfaf.storage.SfPrefilterBacktracePath object with the given
    pattern or None if not found.
    """

    return (db.session.query(st.SfPrefilterBacktracePath)
            .filter(st.SfPrefilterBacktracePath.pattern == pattern)
            .first())


def get_sf_prefilter_btpaths_by_solution(db, db_solution):
    """
    Return a list of pyfaf.storage.SfPrefilterBacktracePath objects
    with the given pyfaf.storage.SfPrefilterSolution or None if not found.
    """

    return (db.session.query(st.SfPrefilterBacktracePath)
            .filter(st.SfPrefilterBacktracePath.solution == db_solution)
            .all())


def get_sf_prefilter_btpaths(db, db_opsys=None):
    """
    Return a list of pyfaf.storage.SfPrefilterBacktracePath objects that apply
    to a given operating system.
    """

    return (db.session.query(st.SfPrefilterBacktracePath)
            .filter((st.SfPrefilterBacktracePath.opsys_id.is_(None)) |
                    (st.SfPrefilterBacktracePath.opsys == db_opsys))
            .all())


def get_sf_prefilter_pkgname_by_pattern(db, pattern):
    """
    Return a pyfaf.storage.SfPrefilterPackageName object with the given
    pattern or None if not found.
    """

    return (db.session.query(st.SfPrefilterPackageName)
            .filter(st.SfPrefilterPackageName.pattern == pattern)
            .first())


def get_sf_prefilter_pkgnames_by_solution(db, db_solution):
    """
    Return a list of pyfaf.storage.SfPrefilterPackageName objects
    with the given pyfaf.storage.SfPrefilterSolution or None if not found.
    """

    return (db.session.query(st.SfPrefilterPackageName)
            .filter(st.SfPrefilterPackageName.solution == db_solution)
            .all())


def get_sf_prefilter_pkgnames(db, db_opsys=None):
    """
    Return a list of pyfaf.storage.SfPrefilterBacktracePath objects that apply
    to a given operating system.
    """

    return (db.session.query(st.SfPrefilterPackageName)
            .filter((st.SfPrefilterPackageName.opsys_id.is_(None)) |
                    (st.SfPrefilterPackageName.opsys == db_opsys))
            .all())


def get_sf_prefilter_sol(db, key):
    """
    Return pyfaf.storage.SfPrefilterSolution object for a given key
    (numeric ID or textual cause) or None if not found.
    """

    try:
        sf_prefilter_sol_id = int(key)
        return get_sf_prefilter_sol_by_id(db, sf_prefilter_sol_id)
    except (ValueError, TypeError):
        return get_sf_prefilter_sol_by_cause(db, key)


def get_sf_prefilter_sols(db):
    """
    Return list of all pyfaf.storage.SfPrefilterSolution objects.
    """

    return (db.session.query(st.SfPrefilterSolution)
            .all())


def get_sf_prefilter_sol_by_cause(db, cause):
    """
    Return pyfaf.storage.SfPrefilterSolution object for a given
    textual cause or None if not found.
    """

    return (db.session.query(st.SfPrefilterSolution)
            .filter(st.SfPrefilterSolution.cause == cause)
            .first())


def get_sf_prefilter_sol_by_id(db, solution_id):
    """
    Return pyfaf.storage.SfPrefilterSolution object for a given
    ID or None if not found.
    """

    return (db.session.query(st.SfPrefilterSolution)
            .filter(st.SfPrefilterSolution.id == solution_id)
            .first())


def get_kernelmodule_by_name(db, module_name):
    """
    Return pyfaf.storage.KernelModule from module name or None if not found.
    """

    return (db.session.query(st.KernelModule)
            .filter(st.KernelModule.name == module_name)
            .first())


def get_packages_by_osrelease(db, name, version, arch):
    """
    Return pyfaf.storage.Package objects assigned to specific osrelease
    specified by name and version or None if not found.
    """

    return (db.session.query(st.Package)
            .join(st.Build)
            .join(st.BuildOpSysReleaseArch)
            .join(st.OpSysRelease)
            .join(st.OpSys)
            .join(st.Arch, st.Arch.id == st.BuildOpSysReleaseArch.arch_id)
            .filter(st.OpSys.name == name)
            .filter(st.OpSysRelease.version == version)
            .filter(st.Arch.name == arch)
            .all())


def get_package_by_file(db, filename):
    """
    Return pyfaf.storage.Package object providing the file named `filename`
    or None if not found.
    """

    return (db.session.query(st.Package)
            .join(st.PackageDependency)
            .filter(st.PackageDependency.name == filename)
            .filter(st.PackageDependency.type == "PROVIDES")
            .first())


def get_packages_by_file(db, filename):
    """
    Return a list of pyfaf.storage.Package objects
    providing the file named `filename`.
    """

    return (db.session.query(st.Package)
            .join(st.PackageDependency)
            .filter(st.PackageDependency.name == filename)
            .filter(st.PackageDependency.type == "PROVIDES")
            .all())


def get_package_by_file_build_arch(db, filename, db_build, db_arch):
    """
    Return pyfaf.storage.Package object providing the file named `filename`,
    belonging to `db_build` and of given architecture, or None if not found.
    """

    return (db.session.query(st.Package)
            .join(st.PackageDependency)
            .filter(st.Package.build == db_build)
            .filter(st.Package.arch == db_arch)
            .filter(st.PackageDependency.name == filename)
            .filter(st.PackageDependency.type == "PROVIDES")
            .first())


def get_packages_by_file_builds_arch(db, filename, db_build_ids,
                                     db_arch, abspath=True):
    """
    Return a list of pyfaf.storage.Package object providing the file named
    `filename`, belonging to any of `db_build_ids` and of given architecture.
    If `abspath` is True, the `filename` must match the RPM provides entry.
    If `abspath` is False, the `filename` must be a suffix of the RPM entry.
    """

    query_base = (db.session.query(st.Package)
                  .join(st.PackageDependency)
                  .filter(st.Package.build_id.in_(db_build_ids))
                  .filter(st.Package.arch == db_arch)
                  .filter(st.PackageDependency.type == "PROVIDES"))

    if abspath:
        return query_base.filter(st.PackageDependency.name == filename).all()

    wildcard = "%/{0}".format(filename)
    return query_base.filter(st.PackageDependency.name.like(wildcard)).all()


def get_package_by_name_build_arch(db, name, db_build, db_arch):
    """
    Return pyfaf.storage.Package object named `name`,
    belonging to `db_build` and of given architecture, or None if not found.
    """

    return (db.session.query(st.Package)
            .filter(st.Package.build == db_build)
            .filter(st.Package.arch == db_arch)
            .filter(st.Package.name == name)
            .first())


def get_package_by_nevra(db, name, epoch, version, release, arch):
    """
    Return pyfaf.storage.Package object from NEVRA or None if not found.
    """

    return (db.session.query(st.Package)
            .join(st.Build)
            .join(st.Arch)
            .filter(st.Package.name == name)
            .filter(st.Build.epoch == epoch)
            .filter(st.Build.version == version)
            .filter(st.Build.release == release)
            .filter(st.Arch.name == arch)
            .first())


def get_build_by_nevr(db, name, epoch, version, release):
    """
    Return pyfaf.storage.Build object from NEVR or None if not found.
    """

    return (db.session.query(st.Build)
            .filter(st.Build.base_package_name == name)
            .filter(st.Build.epoch == epoch)
            .filter(st.Build.version == version)
            .filter(st.Build.release == release)
            .first())


def get_release_ids(db, opsys_name=None, opsys_version=None):
    """
    Return list of `OpSysRelease` ids optionally filtered
    by `opsys_name` and `opsys_version`.
    """

    return [opsysrelease.id for opsysrelease in
            get_releases(db, opsys_name, opsys_version).all()]


def get_repos_for_opsys(db, opsys_id):
    """
    Return Repos assigned to given `opsys_id`.
    """
    return (db.session.query(st.Repo)
            .join(st.OpSysRepo)
            .filter(st.OpSysRepo.opsys_id == opsys_id)
            .all())


def get_src_package_by_build(db, db_build):
    """
    Return pyfaf.storage.Package object, which is the source package
    for given pyfaf.storage.Build or None if not found.
    """

    return (db.session.query(st.Package)
            .join(st.Arch)
            .filter(st.Package.build == db_build)
            .filter(st.Arch.name == "src")
            .first())


def get_ssource_by_bpo(db, build_id, path, offset):
    """
    Return pyfaf.storage.SymbolSource object from build id,
    path and offset or None if not found.
    """

    return (db.session.query(st.SymbolSource)
            .filter(st.SymbolSource.build_id == build_id)
            .filter(st.SymbolSource.path == path)
            .filter(st.SymbolSource.offset == offset)
            .first())


def get_ssources_for_retrace(db, problemtype):
    """
    Return a list of pyfaf.storage.SymbolSource objects of given
    problem type that need retracing.
    """

    return (db.session.query(st.SymbolSource)
            .join(st.ReportBtFrame)
            .join(st.ReportBtThread)
            .join(st.ReportBacktrace)
            .join(st.Report)
            .filter(st.Report.type == problemtype)
            .filter((st.SymbolSource.symbol_id.is_(None)) |
                    (st.SymbolSource.source_path.is_(None)) |
                    (st.SymbolSource.line_number.is_(None)))
            .all())


def get_symbol_by_name_path(db, name, path):
    """
    Return pyfaf.storage.Symbol object from symbol name
    and normalized path or None if not found.
    """

    return (db.session.query(st.Symbol)
            .filter(st.Symbol.name == name)
            .filter(st.Symbol.normalized_path == path)
            .first())


def get_symbolsource(db, symbol, filename, offset):
    """
    Return pyfaf.storage.SymbolSource object from pyfaf.storage.Symbol,
    file name and offset or None if not found.
    """
    if not symbol.id:
        return None

    return (db.session.query(st.SymbolSource)
            .filter(st.SymbolSource.symbol == symbol)
            .filter(st.SymbolSource.path == filename)
            .filter(st.SymbolSource.offset == offset)
            .first())


def get_taint_flag_by_ureport_name(db, ureport_name):
    """
    Return pyfaf.storage.KernelTaintFlag from flag name or None if not found.
    """

    return (db.session.query(st.KernelTaintFlag)
            .filter(st.KernelTaintFlag.ureport_name == ureport_name)
            .first())


def get_unknown_opsys(db, name, version):
    """
    Return pyfaf.storage.UnknownOpSys object from name and version
    or None if not found.
    """

    return (db.session.query(st.UnknownOpSys)
            .filter(st.UnknownOpSys.name == name)
            .filter(st.UnknownOpSys.version == version)
            .first())


def get_packages_and_their_reports_unknown_packages(db):
    """
    Return tuples (st.Package, ReportUnknownPackage) that are joined by package name and
    NEVRA through Build of the Package.

    """

    return (db.session.query(st.Package, st.ReportUnknownPackage)
            .join(st.Build, st.Build.id == st.Package.build_id)
            .filter(st.Package.name == st.ReportUnknownPackage.name)
            .filter(st.Package.arch_id == st.ReportUnknownPackage.arch_id)
            .filter(st.Build.epoch == st.ReportUnknownPackage.epoch)
            .filter(st.Build.version == st.ReportUnknownPackage.version)
            .filter(st.Build.release == st.ReportUnknownPackage.release))




def get_bugtracker_by_name(db, name):
    return (db.session.query(st.Bugtracker)
            .filter(st.Bugtracker.name == name)
            .first())


def get_crashed_package_for_report(db, report_id):
    """
    Return Packages that CRASHED in a given report.
    """
    return (db.session.query(st.Package)
            .join(st.ReportPackage.installed_package)
            .filter(st.ReportPackage.installed_package_id == st.Package.id)
            .filter(st.ReportPackage.report_id == report_id)
            .filter(st.ReportPackage.type == "CRASHED")
            .all())


def user_is_maintainer(db, username, component_id):
    return (db.session.query(st.AssociatePeople)
            .join(st.OpSysComponentAssociate)
            .join(st.OpSysComponent)
            .filter(st.AssociatePeople.name == username)
            .filter(st.OpSysComponent.id == component_id)
            .filter(st.OpSysComponentAssociate.permission == "commit")
            .count()) > 0


def get_mantis_bug(db, external_id, tracker_id):
    """
    Return MantisBug instance if there is a bug in the database
    with `(external_id, tracker_id)`.
    """

    return (db.session.query(st.MantisBug)
            .filter(st.MantisBug.external_id == external_id)
            .filter(st.MantisBug.tracker_id == tracker_id)
            .first())


def delete_mantis_bugzilla(db, bug_id):
    """
    Delete Mantis Bugzilla for given bug_id.
    """
    query = (db.session.query(st.MantisBug)
             .filter(st.MantisBug.duplicate_id == bug_id)
             .all())

    for mantisgz in query:
        mantisgz.duplicate_id = None

    db.session.query(st.ReportMantis).filter(st.ReportMantis.mantisbug_id == bug_id).delete(False)
    db.session.query(st.MantisBug).filter(st.MantisBug.id == bug_id).delete(False)

def get_builds_by_opsysrelease_id(db, opsysrelease_id):
    """
    Return all builds, that are assigned to this opsysrelease but none other,
    architecture is missed out intentionally.
    """
    bosra1 = aliased(st.BuildOpSysReleaseArch)
    bosra2 = aliased(st.BuildOpSysReleaseArch)

    return (db.session.query(bosra1)
            .filter(bosra1.opsysrelease_id == opsysrelease_id)
            .filter(~bosra1.build_id.in_(
                db.session.query(bosra2.build_id)
                .filter(bosra1.build_id == bosra2.build_id)
                .filter(bosra2.opsysrelease_id != opsysrelease_id)
                ))
            .all())
