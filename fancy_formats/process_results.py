from abc import ABC, abstractmethod

from fancy_formats import xml_classes


# See: https://github.com/international-orienteering-federation/datastandard-v3
file_path = "../../datastandard-v3-master/examples/ResultList1.xml"


class Format(ABC):
    """A base class defining the required behaviour of all results analysis formats."""
    def __init__(self):
        if not vars(self):
            error_msg = f"No input arguments provided for {type(self).__name__} class"
            raise ValueError(error_msg)
        super().__init__()

    @abstractmethod
    def analyse(self):
        pass


class OddsEvens(Format):
    """Analyse the results of a score in line with the odds and evens format."""
    def __init__(self):
        self.penalty_type: str = "points"
        self.penalty_per: int = 10

        super().__init__()

    def analyse(self):
        pass

# rootObject = xml_classes.parse(file_path, silence=True)
# for class_result in rootObject.ClassResult:
#     for person_result in class_result.PersonResult:
#         person = person_result.Person
#         person_name = person.Name
#         print(" ".join((person_name.Given, person_name.Family)))
