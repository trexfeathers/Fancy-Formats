from os import path
from xml.etree import ElementTree
from datetime import datetime
import pprint


def import_xml(file_path):
    if path.exists(file_path):
        file_xml = ElementTree.parse(file_path)
        return file_xml
    else:
        raise Exception('Path does not exist')


def get_course(xml_root, result_index):
    return xml_root[result_index + 1]


def process_course(xml_course: ElementTree.Element):
    def replace_none(possible_none, data_type: type):
        if data_type == str:
            return_val = ''
        elif data_type == int:
            return_val = 0
        else:
            return_val = None

        return return_val if possible_none is None else possible_none

    prefix = '{http://www.orienteering.org/datastandard/3.0}'
    results_list = []
    for person in xml_course.findall(prefix + 'PersonResult'):
        results_dict = {}
        basics = person.find(prefix + 'Person')
        gender = basics.get('sex')
        gender = 'W' if gender == 'F' else gender
        dob = basics.find(prefix + 'BirthDate').text
        if dob:
            dob = datetime.strptime(dob, '%Y-%m-%d')
            age = datetime.now().year - dob.year
        else:
            age = 0
        results_dict['class'] = gender + str(age)

        name_tree = basics.find(prefix + 'Name')
        name_first = replace_none(name_tree.find(prefix + 'Given').text, str)
        name_last = replace_none(name_tree.find(prefix + 'Family').text, str)
        results_dict['name'] = name_first + ' ' + name_last

        club = person.find(prefix + 'Organisation').find(prefix + 'Name').text
        results_dict['club'] = replace_none(club, str)

        # result_list = []
        result_ok = False
        result_tree = person.find(prefix + 'Result')
        if result_tree:
            result_status = result_tree.find(prefix + 'Status').text
            if result_status:
                result_ok = result_status == 'OK'

            score = replace_none(result_tree.find(prefix + 'Score'), int)
            secs = replace_none(result_tree.find(prefix + 'Time'), int)

            control_list = []
            for control in result_tree.findall(prefix + 'SplitTime'):
                control_code = control.find(prefix + 'ControlCode').text
                if control_code:
                    control_list.append(control_code)
            results_dict['control_sequence'] = control_list
            results_dict['bad_controls'] = odds_evens(control_list)

        results_dict['status_ok'] = result_ok

        results_list.append(results_dict)

    return results_list


def odds_evens(controls_list: list):
    def control_is_odd(control_number):
        return bool(int(control_number) % 2)

    bad_controls = 0
    odd_mode = control_is_odd(controls_list[0])
    has_switched = False
    for control in controls_list[1:]:
        if odd_mode != control_is_odd(control):
            if not has_switched:
                has_switched = True
                odd_mode = control_is_odd(control)
            else:
                bad_controls += 1

    return bad_controls


if __name__ == '__main__':
    xml = import_xml('Sample.xml')
    course_index = 1
    root = xml.getroot()
    course = get_course(root, course_index)
    results = process_course(course)
    # pprint.pprint(process_course(course))

