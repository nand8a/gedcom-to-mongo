import logging
import pprint
log = logging.getLogger(__name__)
import utils
import re

pp = pprint.PrettyPrinter(indent=4)


def _children(lines, i):
    children_list = []
    while i < len(lines) and '1 CHIL' in lines[i]:
        child = re.search(r"@[A-Z0-9]*@", lines[i]).group(0)
        children_list.append(child)
        i += 1
    return children_list, i


def parser(lines):
    family_dict = {}
    i = 0
    while i < len(lines):
        if bool(re.search('0 @[A-Z0-9]*@ FAM', lines[i])):
            identifier = lines[i].split(' ')[1]
            log.debug('FAM: {}'.format(identifier))
            family_dict['_id'] = identifier
            i += 1
        elif lines[i].startswith('1'):
            if '1 CHIL' in lines[i]:
                key = 'chil'
                if key not in family_dict:
                    family_dict[key] = []
                child_list, i = _children(lines, i)
                family_dict[key] += child_list
            else:  # todo - not dry - move to that function
                local_dict, i = utils.ged_sub_structure(lines, i, lines[i].split(' ')[0])
                family_dict.update(local_dict)
                key = list(local_dict.keys())[0]
                while i < len(lines) and (lines[i].split(' ')[0] != '1'):
                    local_dict, i = utils.ged_sub_structure(lines, i, lines[i].split(' ')[0])
                    family_dict[key] = local_dict
        else:
            current_level = lines[i][0]
            ret_dict, i = utils.ged_sub_structure(lines, i, current_level)
            family_dict.update(ret_dict)
    log.debug(pp.pprint(family_dict))
    return family_dict

