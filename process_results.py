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
    def replace_none(possible_none):
        return '' if possible_none is None else possible_none

    prefix = '{http://www.orienteering.org/datastandard/3.0}'
    results_list = []
    for person in xml_course.findall(prefix + 'PersonResult'):
        results_dict = {}
        basics = person.find(prefix + 'Person')
        gender = basics.get('sex')
        dob = basics.find(prefix + 'BirthDate').text
        if dob:
            dob = datetime.strptime(dob, '%Y-%m-%d')
            age = datetime.now().year - dob.year
        else:
            age = 0
        results_dict['class'] = gender + str(age)

        name_tree = basics.find(prefix + 'Name')
        name_first = replace_none(name_tree.find(prefix + 'Given').text)
        name_last = replace_none(name_tree.find(prefix + 'Family').text)
        results_dict['name'] = name_first + ' ' + name_last

        results_dict['club'] = person.find(
            prefix + 'Organisation').find(
                prefix + 'Name').text

        results_list.append(results_dict)

    return results_list


if __name__ == '__main__':
    xml = import_xml('Sample.xml')
    course_index = 1
    root = xml.getroot()
    course = get_course(root, course_index)
    pprint.pprint(process_course(course))

