import logging
import pprint

from dbinterface import *
import settings

log = logging.getLogger(__name__)

pp = pprint.PrettyPrinter(indent=4)

__proc_name__ = 'embed_p1'


# the processor needs to write somewhere. it should write to a store
# the processor should get data from the store, act/change it, then write it back
# this should perhaps be that the processor doesn't contain reference to the store, it is
# simply given data, then returns that data
def processor(family_coll: MongoDb, person_coll: MongoDb):
    """
    run over the family database and embed some of the values in the person database.
    The purpose of this embedding module is to be a replayable pipeline. There are currently
    two databases, person and family, the ideal is that we only have one (namely person), but
    until it is clear that we have understood all the queries correctly, we are going to keep
    that family collection (as an aside, this could ultimately be moved up the chain so that
    we process the family section without writing it to a db first).s
    :return:
    """
    # get a generator from the family collection
    fam_gen = family_coll.read_unprocessed(__proc_name__)
    count = 0
    try:
        # iterate over the family records and embed in person records
        while True:
            fam_record = next(fam_gen)
            # get children out of record
            if 'chil' in fam_record:
                children = fam_record['chil']
            else:
                children = []
            # get parents out of family record
            parents = _get_parents_from_family(fam_record)
            # for each parent embed in person collection (married_count, spouses list and children_count)
            for parent in parents:
                parent_record = person_coll.read_parent_family_counts(parent)
                spouses = _get_spouses(parents, parent, parent_record)
                parent_dict = _get_update_parent_dict(parent, len(children), spouses)
                person_coll.write_update(parent, parent_dict)
            # for each child, embed in person collection (add to their parent list)
            for child in children:
                child_record = person_coll.read_person(child)
                if 'parents' in child_record.keys():
                    existing_parents = child_record['parents']
                else:
                    existing_parents = []
                new_parent_list = _update_children(existing_parents, parents, children)
                person_coll.write_update(child, {'parents': new_parent_list})
            count += 1
            family_coll.write_processor(fam_record['_id'], __proc_name__)
    except StopIteration as e:
        pass

    #        if count == 10:
    #            break
    log.info('processed {} records with {} processor'.format(count, __proc_name__))


def _update_children(existing_parents, parents: list, children: list):
    for child in children:
        # just for caution sake
        if existing_parents:
            log.error('{} has multiple parents... is this possible?'.format(child))
            log.error('attempting to insert parents {}'.format(parents))
            # raise ValueError('Assumption is that children may not have multiple parents')
            return_parents = parents + existing_parents
            print('---------return_parents {}'.format(return_parents))
            return return_parents
        return parents


def _get_spouses(parents: list, current_parent: str, current_record: dict):
    """
    given a list of parents, of which current_parent is a member,
    extract the spouses from current_record and return the list of the
    spouses only
    :param parents: a list of parent identifiers
    :param current_parent: a single parent identifier which is also in the parents list
    :param current_record: a record that may already contain spouses, e.g. {'spouses': ['@I1']}
    """
    # we are assuming that there are two parents in each case
    if len(parents) > 2:
        raise NotImplementedError('We are not catering for more than two parents in a single family')
    spouses = list(set(parents) - set([current_parent]))
    log.debug('spouses list {}'.format(spouses))
    if 'spouses' in current_record:
        spouses += current_record['spouses']
    return spouses


# todo - it smells a little to update nr married, nr children and then to pass through spouses
# problem is that spouses acts on the entire parents list...
def _get_update_parent_dict(parent_record: dict, nr_of_children: int, spouses: list):
    """
    Increment the married counter, add the nr of children and replace the existing
    spouses with the spouses list passed in.
    :param parent_record: the parent record for the parent currently under consideratio n
    :param nr_of_children: a scalar number of children in this current family iteration
    :param spouses: currently just a pass through to build the dictionary
    :return: a dictionary containing the updated fields *only*, i.e. 'married_count', 'children_count'
    and 'spouses'
    """
    married_count = 1
    if 'married_count' in parent_record:
        married_count += parent_record['married_count']
    children_count = nr_of_children
    if 'children_count' in parent_record:
        children_count += parent_record['children_count']

    update_dict = {'married_count': married_count,
                   'children_count': children_count,
                   'spouses': spouses}

    return update_dict


# todo - this should live in the mongodb child object that manages
# just the family database queries - that would sort out these annoying keys too
# it is not clear what value this is adding here - pleeeeease move :-|
def _get_parents_from_family(record: dict):
    """
    Given a family record, extract the parents
    :param record:
    :return:
    """
    parents = []
    try:
        parents.append(record['husb'])
    except KeyError as e:
        # todo - this log warning would assume we have the record_id - should be managed by familyDb
        # log.warning('no husband in family {}'.format(record['_id']))
        log.debug('no husband exception {}'.format(e))
    try:
        parents.append(record['wife'])
    except KeyError as e:
        # log.warning('no wife in family {}'.format(record['_id']))
        log.debug('no wife exception {}'.format(e))
    return parents

