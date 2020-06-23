from abc import ABC, abstractmethod
from inspect import signature

from fancy_formats import xml_classes


# See: https://github.com/international-orienteering-federation/datastandard-v3
file_path = "../../datastandard-v3-master/examples/ResultList1.xml"


class Format(ABC):
    """
    A base class defining the required behaviour of all results analysis formats.

    .. note:: Correct sub-class implementation:
    * __init__ must include at least one parameter
    * all parameters must have type annotations
    * __init__ must end with super().__init__()
    """
    @abstractmethod
    def __init__(self):
        params = signature(type(self)).parameters
        if not params:
            error_msg = f"No input parameters specified in {type(self).__name__} class"
            raise ValueError(error_msg)
        super().__init__()

    @abstractmethod
    def analyse(self):
        pass


class OddsEvens(Format):
    """Analyse the results of a score in line with the odds and evens format."""
    def __init__(self,
                 penalty_type: str = "points",
                 penalty_per: int = 10):
        super().__init__()

    def analyse(self):
        pass

# rootObject = xml_classes.parse(file_path, silence=True)
# for class_result in rootObject.ClassResult:
#     for person_result in class_result.PersonResult:
#         person = person_result.Person
#         person_name = person.Name
#         print(" ".join((person_name.Given, person_name.Family)))
