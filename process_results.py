# Script to process xml orienteering score results for unusual formats such as
# Harris relays, odds & evens etc.

from os import path
from xml.etree import ElementTree
from datetime import datetime


def import_xml(file_path):
    # Get parsed xml from a given file path.
    if path.exists(file_path):
        file_xml = ElementTree.parse(file_path)
        return file_xml
    else:
        raise Exception('Path does not exist')


def get_course(xml_root, result_index):
    # Single out an individual course from xml results.
    return xml_root[result_index + 1]


def process_course(xml_course: ElementTree.Element, result_type: str):
    # Pick out desired details from course xml and store in a usable format.
    def replace_none(possible_none, data_type: type):
        # Replace None values with populated equivalent dependent on data type.
        if data_type == str:
            return_val = ''
        elif data_type == int:
            return_val = 0
        else:
            return_val = None

        return return_val if possible_none is None else possible_none

    # All XML elements names are preceeded with the prefix.
    prefix = '{http://www.orienteering.org/datastandard/3.0}'
    results_list = []
    for person in xml_course.findall(prefix + 'PersonResult'):
        results_dict = {}
        basics = person.find(prefix + 'Person')

        # Construct age class from several XML elements.
        gender = basics.get('sex')
        gender = 'W' if gender == 'F' else gender
        dob = basics.find(prefix + 'BirthDate').text
        if dob:
            dob = datetime.strptime(dob, '%Y-%m-%d')
            age = datetime.now().year - dob.year
        else:
            age = 0
        results_dict['class'] = gender + str(age)

        # Stitch a full name string together from the tree of names.
        name_tree = basics.find(prefix + 'Name')
        name_first = replace_none(name_tree.find(prefix + 'Given').text, str)
        name_last = replace_none(name_tree.find(prefix + 'Family').text, str)
        results_dict['name'] = name_first + ' ' + name_last

        # Get the competitor's club.
        club = person.find(prefix + 'Organisation').find(prefix + 'Name').text
        results_dict['club'] = replace_none(club, str)

        # result_ok will only turn to true if there is no reason to flag it.
        result_ok = False
        result_tree = person.find(prefix + 'Result')
        if result_tree:
            result_status = result_tree.find(prefix + 'Status').text
            if result_status:
                result_ok = result_status == 'OK'

            # Extract the original score and time before any post-processing.
            score = replace_none(result_tree.find(prefix + 'Score'), int)
            secs = replace_none(result_tree.find(prefix + 'Time'), int)

            # Process the tree of control times into a list of control codes.
            control_list = []
            for control in result_tree.findall(prefix + 'SplitTime'):
                control_code = control.find(prefix + 'ControlCode').text
                if control_code:
                    control_list.append(control_code)
            results_dict['control_sequence'] = control_list

            # Identify any invalid controls depending on the format.
            results_dict['bad_controls'] = []
            if result_type == 'odds and evens':
                results_dict['bad_controls'] = odds_evens(control_list)

        # Mark whether the result is valid.
        results_dict['status_ok'] = result_ok

        # Add this competitor to the full list.
        results_list.append(results_dict)

    return results_list


def odds_evens(controls_list: list):
    # Check a list of control codes for conformance with the odds and evens
    # score format.

    def control_is_odd(control_number):
        return bool(int(control_number) % 2)

    bad_controls = 0
    # Identify starting control set.
    odd_mode = control_is_odd(controls_list[0])
    has_switched = False

    for control in controls_list[1:]:
        if odd_mode != control_is_odd(control):
            # Have identified a switch from one control set to the other.
            if not has_switched:
                # Is a valid switch since this is the first time.
                has_switched = True
                odd_mode = control_is_odd(control)
            else:
                # Competitor switched earlier so this is against the rules.
                bad_controls += 1

    return bad_controls


def demo():
    xml = import_xml('Sample.xml')
    course_index = 1
    root = xml.getroot()
    course = get_course(root, course_index)
    results = process_course(course, result_type='odds and evens')
    print(results)


if __name__ == '__main__':
    demo()
