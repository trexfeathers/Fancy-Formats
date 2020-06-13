from fancy_formats import xml_classes

file_path = "/examples/ResultList1.xml"
rootObject = xml_classes.parse(file_path, silence=True)

for class_result in rootObject.ClassResult:
    for person_result in class_result.PersonResult:
        person = person_result.Person
        person_name = person.Name
        print(" ".join((person_name.Given, person_name.Family)))
