# Script to process xml orienteering score results for unusual formats such as
# Harris relays, odds & evens etc.

from os import path
from xml.etree import ElementTree
from datetime import datetime, timedelta
from csv import writer

# All XML elements names are preceeded with the prefix.
prefix = '{http://www.orienteering.org/datastandard/3.0}'


class IofEvent:
    def __init__(self, file_path: str):
        if path.exists(file_path):
            file_xml = ElementTree.parse(file_path)
            self.xml_root = file_xml.getroot()
        else:
            raise TypeError('No valid xml found at given path.')

        info_tree = self.xml_root.find(prefix + 'Event')
        if info_tree:
            self.event_name = info_tree.find(prefix + 'Name').text
        if not self.event_name:
            raise ValueError('No event name found.')

        if self.xml_root:
            self.course_list = []
            for ix, course in enumerate(
                    self.xml_root.findall(prefix + 'ClassResult')):
                course_info = course.find(prefix + 'Class')
                course_name = course_info.find(prefix + 'Name').text
                course_xml = self.xml_root[ix + 1]
                if course_name:
                    self.course_list.append(IofCourse(course_name, course_xml))
            if len(self.course_list) == 0:
                raise ValueError('No courses found in event.')

    def list_courses(self):
        return [course.course_name for course in self.course_list]


class IofCourse:
    def __init__(self, course_name: str, xml_course: ElementTree.Element):
        self.course_name = course_name
        self.person_result_list = []
        for person_result in xml_course.findall(prefix + 'PersonResult'):
            self.person_result_list.append(IofPersonResult(person_result))

        self.format_options = {
            '"Odds and Evens"': self.evaluate_odds_evens
        }

    def check_for_results(self):
        if len(self.person_result_list) == 0:
            raise ValueError('No results found in course.')

    def evaluate_odds_evens(self,
                            file_path: str,
                            penalty_type: str,
                            penalty_per: int):
        
        self.check_for_results()

        if penalty_type == 'points':
            name_penalty_total = 'penalty points'
            name_final = 'FINAL SCORE'
        elif penalty_type == 'seconds':
            name_penalty_total = 'penalty seconds'
            name_final = 'FINAL TIME'

        csv_headers = ['name',
                       'class',
                       'club',
                       'time',
                       'score',
                       'penalty count',
                       name_penalty_total,
                       name_final,
                       'control sequence',
                       'penalty controls']

        # Add spacers for CSV.
        for i in (8, 5):
            csv_headers.insert(i, '')
        csv_content = []

        for person_result in self.person_result_list:
            penalty_controls = _odds_evens(person_result.control_sequence)
            penalty_count = len(penalty_controls)
            penalty_total = penalty_count * penalty_per
            if penalty_type == 'points':
                penalty_display = f'-{str(penalty_total)}'
                final_display = person_result.points - penalty_total
            elif penalty_type == 'seconds':
                penalty_display = f'+{str(penalty_total)}'
                final_seconds = person_result.seconds + penalty_total
                final_display = timedelta(seconds=final_seconds)

            csv_row_dict = {'name': person_result.name,
                            'class': person_result.age_class,
                            'club': person_result.club,
                            'time': timedelta(seconds=person_result.seconds),
                            'score': person_result.points,
                            'penalty count': penalty_count,
                            name_penalty_total: penalty_display,
                            name_final: final_display,
                            'control sequence': person_result.control_sequence,
                            'penalty controls': penalty_controls}
            csv_row_list = [None] * len(csv_headers)
            for key, value in csv_row_dict.items():
                ix = csv_headers.index(key)
                csv_row_list[ix] = value
            csv_content.append(csv_row_list)
            
        _csv_export(file_path, csv_headers, csv_content)
        return True


class IofPersonResult:
    def __init__(self, xml_person_result: ElementTree.Element):
        basics = xml_person_result.find(prefix + 'Person')

        # Construct age class from several XML elements.
        gender = basics.get('sex')
        gender = 'W' if gender == 'F' else gender
        dob = basics.find(prefix + 'BirthDate').text
        if dob:
            dob = datetime.strptime(dob, '%Y-%m-%d')
            age = datetime.now().year - dob.year
        else:
            age = 0
        self.age_class = gender + str(age)

        # Stitch a full name string together from the tree of names.
        name_tree = basics.find(prefix + 'Name')
        name_first = _replace_none(
            name_tree.find(prefix + 'Given').text, str)
        name_last = _replace_none(
            name_tree.find(prefix + 'Family').text, str)
        self.name = name_first + ' ' + name_last

        # Get the competitor's club.
        club = xml_person_result.find(
            prefix + 'Organisation').find(prefix + 'Name').text
        self.club = _replace_none(club, str)

        # result_ok will only turn to true if there is no reason to flag it.
        result_ok = False
        result_tree = xml_person_result.find(prefix + 'Result')
        if result_tree:
            result_status = result_tree.find(prefix + 'Status').text
            if result_status:
                result_ok = result_status == 'OK'

            # Extract the original score and time before any post-processing.
            self.points = _replace_none(
                int(result_tree.find(prefix + 'Score').text), int)
            self.seconds = _replace_none(
                int(result_tree.find(prefix + 'Time').text), int)

            # Process the tree of control times into a list of control codes.
            self.control_sequence = []
            for control in result_tree.findall(prefix + 'SplitTime'):
                control_code = control.find(prefix + 'ControlCode').text
                if control_code:
                    self.control_sequence.append(control_code)

        # Mark whether the result is valid.
        self.status_ok = result_ok


def import_xml(file_path):
    # Get parsed xml from a given file path.
    if path.exists(file_path):
        file_xml = ElementTree.parse(file_path)
        xml_root = file_xml.getroot()
        return xml_root
    else:
        raise TypeError('No valid xml found at given path.')


def list_courses(results_xml: ElementTree.Element):
    # List all courses held within the xml results.
    course_list = []
    for course in results_xml.findall(prefix + 'ClassResult'):
        course_info = course.find(prefix + 'Class')
        course_name = course_info.find(prefix + 'Name').text
        if course_name:
            course_list.append(course_name)

    return course_list


def get_course(results_xml, result_index):
    # Single out an individual course from xml results.
    return results_xml[result_index]


def get_title(results_xml: ElementTree.Element):
    info_tree = results_xml.find(prefix + 'Event')
    if info_tree:
        event_name = info_tree.find(prefix + 'Name').text
        if event_name:
            return event_name

    raise Exception('No event name found.')


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

            # # Identify any invalid controls depending on the format.
            # results_dict['penalty_controls'] = []
            # if result_type == 'odds and evens':
            #     results_dict['penalty_controls'] = odds_evens(control_list)

        # Mark whether the result is valid.
        results_dict['status_ok'] = result_ok

        # Add this competitor to the full list.
        results_list.append(results_dict)

    return results_list


# def odds_evens(controls_list: list):
def _odds_evens(control_sequence: list):
    # Check a list of control codes for conformance with the odds
    # and evens score format.

    def control_is_odd(control_number):
        return bool(int(control_number) % 2)

    penalty_controls = []
    # Identify starting control set.
    odd_mode = control_is_odd(control_sequence[0])
    has_switched = False

    for control in control_sequence[1:]:
        if odd_mode != control_is_odd(control):
            # Have identified a switch from one control set to the
            # other.
            if not has_switched:
                # Is a valid switch since this is the first time.
                has_switched = True
                odd_mode = control_is_odd(control)
            else:
                # Competitor switched earlier so this is against
                # the rules.
                penalty_controls.append(control)

    return penalty_controls


def _csv_export(file_path: str, headers: list, content: list):
    file_path = path.normpath(file_path)
    if not \
            all([isinstance(header, str) for header in headers]) and \
            all([isinstance(column, list) for column in content]):
        raise TypeError('Unexpected output format.')
    else:
        with open(file_path, 'w+') as csv_file:
            csv_writer = writer(csv_file, lineterminator='\n')
            csv_writer.writerow(headers)
            for row in content:
                csv_writer.writerow(row)

    print(f'File written to {file_path}.')


def _replace_none(possible_none, data_type: type):
    # Replace None values with populated equivalent dependent on data type.
    if data_type == str:
        return_val = ''
    elif data_type == int:
        return_val = 0
    else:
        return_val = None

    return return_val if possible_none is None else possible_none


def demo():
    # results_xml = import_xml('Sample.xml')
    # print(list_courses(results_xml))
    # course_index = 1
    # course = get_course(results_xml, course_index)
    # results = process_course(course, result_type='odds and evens')
    # print(results)
    event = IofEvent('Sample.xml')
    course = event.course_list[0]
    course.evaluate_odds_evens('export.csv', 'seconds', 60)


if __name__ == '__main__':
    demo()
