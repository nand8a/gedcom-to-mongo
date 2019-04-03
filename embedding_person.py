import logging
import pprint

from dbinterface import Db

log = logging.getLogger(__name__)

pp = pprint.PrettyPrinter(indent=4)

__proc_name__ = 'embed_p1'


def processor():
    """
    run over the family database and embed some of the values in the person database.
    The purpose of this embedding module is to be a replayable pipeline. There are currently
    two databases, person and family, the ideal is that we only have one (namely person), but
    until it is clear that we have understood all the queries correctly, we are going to keep
    that family collection (as an aside, this could ultimately be moved up the chain so that
    we process the family section without writing it to a db first).s
    :return:
    """
    family_coll = Db().get_connect().collection('gedcom', 'fam_test')
    person_coll = Db().get_connect().collection('gedcom', 'person_test')
    # get a mongo cursor
    cursor = family_coll.find(
        {'processors': {'$not': {'$elemMatch': {'$regex': __proc_name__}}}}
    )
    record = cursor.next()
    count = 0
    while record:
        # get children out of record
        if 'chil' in record:
            children = record['chil']
        else:
            children = []
        parents = _get_parents(record)
        # goto parents and increment their marriage counters
        _update_parents(parents, len(children), person_coll)
        # for each of the children, provide these as the parents
        _update_children(person_coll, parents, children)
        count += 1
        # ok, everything is done, update that is has been processed
        # todo - need to perform at the start too - harden
        family_coll.find_one_and_update(
            {'_id': record['_id']},
            {"$set": {'processors': [__proc_name__]}}, upsert=True)

        record = cursor.next()
#        if count == 10:
#            break
    log.info('processed {} records with {} processor'.format(count, __proc_name__))


def _update_children(person_coll, parents: list, children: list):
    for child in children:
        # just for caution sake

        if person_coll.find_one({'_id': child, 'parents': {'$exists': True, '$ne': []}}):
            log.error('{} has multiple parents... is this possible?'.format(child))
            log.error('attempting to insert parents {}'.format(parents))
            raise ValueError('Assumption is that children may not have multiple parents')
        person_coll.find_one_and_update(
            {'_id': child},
            {"$set": {'parents': parents}}, upsert=True)


def _get_spouses(parents: list, current_parent: str, current_record: dict):
    """
    given a list of parents, of which current_parent is a member,
    extract the spouses from current_record and return the list of the
    spouses only
    """
    # we are assuming that there are two parents in each case
    if len(parents) > 2:
        raise NotImplementedError('We are not catering for more than two parents in a single family')
    spouses = list(set(parents) - set([current_parent]))
    log.debug('spouses list {}'.format(spouses))
    if 'spouses' in current_record:
        spouses += current_record['spouses']
    return spouses


def _update_parents(parents: list, nr_of_children, person_coll):
    for parent in parents:
        parent_record = person_coll.find_one({'_id': parent},
                                             {'married_count': 1,
                                              'children_count': 1,
                                              'spouses': 1})
        married_count = 1
        if 'married_count' in parent_record:
            married_count += parent_record['married_count']
        log.debug('{}\'s marriage counter is {}. updating in mongo'.format(
            parent, married_count))

        spouses = _get_spouses(parents, parent, parent_record)
        log.debug('new spouses {}'.format(spouses))
        log.debug('{}\'s spouse list is {}'.format(parent, spouses))

        children_count = nr_of_children
        if 'children_count' in parent_record:
            children_count += parent_record['children_count']

        update_dict = {'married_count': married_count,
                       'children_count': children_count,
                       'spouses': spouses}

        person_coll.find_one_and_update(
            {'_id': parent},
            {"$set": update_dict}, upsert=True)


def _get_parents(record: dict):
    parents = []
    try:
        parents.append(record['husb'])
    except KeyError as e:
        log.warning('no husband in family {}'.format(record['_id']))
        log.debug('no husband exception {}'.format(e))
    try:
        parents.append(record['wife'])
    except KeyError as e:
        log.warning('no wife in family {}'.format(record['_id']))
        log.debug('no wife exception {}'.format(e))
    return parents

