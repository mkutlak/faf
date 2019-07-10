def get_problems(db):
    """
    Return a list of all pyfaf.storage.Problem in the storage.
    """

    return (db.session.query(st.Problem)
            .all())

def get_problem_by_id(db, looked_id):
    """
    Return pyfaf.storage.Problem corresponding to id.
    """

    return (db.session.query(st.Problem)
            .filter(st.Problem.id == looked_id)
            .first())


def get_empty_problems(db, yield_num=0):
    """
    Return a list of pyfaf.storage.Problem that have no reports.
    With optional yield_per.
    """
    query = (db.session.query(st.Problem)
             .outerjoin(st.Report)
             .group_by(st.Problem)
             .having(func.count(st.Report.id) == 0))

    if yield_num > 0:
        return query.yield_per(yield_num)

    return query.all()


def query_problems(db, hist_table, opsysrelease_ids, component_ids,
                   rank_filter_fn=None, post_process_fn=None):
    """
    Return problems ordered by history counts
    """

    rank_query = (db.session.query(st.Problem.id.label('id'),
                                   func.sum(hist_table.count).label('rank'))
                  .join(st.Report, st.Report.problem_id == st.Problem.id)
                  .join(hist_table)
                  .filter(hist_table.opsysrelease_id.in_(opsysrelease_ids)))

    if rank_filter_fn:
        rank_query = rank_filter_fn(rank_query)

    rank_query = (rank_query.group_by(st.Problem.id).subquery())

    final_query = (
        db.session.query(st.Problem,
                         rank_query.c.rank.label('count'),
                         rank_query.c.rank)
        .filter(rank_query.c.id == st.Problem.id)
        .order_by(desc(rank_query.c.rank)))

    if component_ids is not None:
        final_query = (
            final_query.join(st.ProblemComponent)
            .filter(st.ProblemComponent.component_id.in_(component_ids)))

    problem_tuples = final_query.all()

    if post_process_fn:
        problem_tuples = post_process_fn(problem_tuples)

    for problem, count, _ in problem_tuples:
        problem.count = count

    return [x[0] for x in problem_tuples]


def query_hot_problems(db, opsysrelease_ids,
                       component_ids=None, last_date=None,
                       history="daily"):
    """
    Return top problems since `last_date` (2 weeks ago by default)
    """

    if last_date is None:
        last_date = datetime.date.today() - datetime.timedelta(days=14)

    hist_table, hist_field = get_history_target(history)

    return query_problems(db,
                          hist_table,
                          opsysrelease_ids,
                          component_ids,
                          lambda query: query.filter(hist_field >= last_date))


def prioritize_longterm_problems(min_fa, problem_tuples):
    """
    Occurrences holding zero are not stored in the database. In order to work
    out correct average value it is necessary to work out a number of months
    and then divide the total number of occurrences by the worked out sum of
    months. Returned list must be sorted according to priority. The bigger
    average the highest priority.
    """

    for problem, _, rank in problem_tuples:
        months = (min_fa.month - problem.first_occurrence.month) + 1
        if min_fa.year != problem.first_occurrence.year:
            months = (min_fa.month
                      +
                      (12 * (min_fa.year - problem.first_occurrence.year - 1))
                      + (13 - problem.first_occurrence.month))

        if problem.first_occurrence.day != 1:
            months -= 1

        problem.rank = rank / float(months)

# Original Python 2 code:
#   return sorted(problem_tuples, key=lambda (problem, _, __): problem.rank,
#                 reverse=True)
    return sorted(problem_tuples, key=lambda problem_____: problem_____[0].rank,
                  reverse=True)


def query_longterm_problems(db, opsysrelease_ids, component_ids=None,
                            history="monthly"):
    """
    Return top long-term problems
    """

    # minimal first occurrence is the first day of the last month
    min_fo = datetime.date.today().replace(day=1) - datetime.timedelta(days=1)
    min_fo = min_fo.replace(day=1)

    hist_table, hist_field = get_history_target(history)

    return query_problems(
        db,
        hist_table,
        opsysrelease_ids,
        component_ids,
        lambda query: (
            # use only Problems that live at least one whole month
            query.filter(st.Problem.first_occurrence <= min_fo)
            # do not take into account first incomplete month
            .filter(st.Problem.first_occurrence <= hist_field)
            # do not take into account problems that don't have any
            # occurrence since last month
            .filter(st.Problem.id.in_(
                db.session.query(st.Problem.id)
                .join(st.Report)
                .join(hist_table)
                .filter(st.Problem.last_occurrence >= min_fo)
                .subquery()))
        ),
        functools.partial(prioritize_longterm_problems, min_fo))


def get_problem_component(db, db_problem, db_component):
    """
    Return pyfaf.storage.ProblemComponent object from problem and component
    or None if not found.
    """
    if not db_problem.id:
        return None

    return (db.session.query(st.ProblemComponent)
            .filter(st.ProblemComponent.problem == db_problem)
            .filter(st.ProblemComponent.component == db_component)
            .first())


def get_problem_opsysrelease(db, problem_id, opsysrelease_id):
    return (db.session.query(st.ProblemOpSysRelease)
            .filter(st.ProblemOpSysRelease.problem_id == problem_id)
            .filter(st.ProblemOpSysRelease.opsysrelease_id == opsysrelease_id)
            .first())


def get_problemreassigns_by_username(db, username):
    """
    Returns query for ProblemReassign objects for given username.
    """
    return db.session.query(st.ProblemReassign).filter(st.ProblemReassign.username == username)


