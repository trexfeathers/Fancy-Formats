from abc import ABC, abstractmethod
from inspect import _empty as inspect_empty, signature
from pathlib import Path

from fancy_formats import xml_classes


# See: https://github.com/international-orienteering-federation/datastandard-v3
file_path = "../../datastandard-v3-master/examples/ResultList1.xml"


class Format(ABC):
    """
    A base class defining the required behaviour of all results analysis formats.

    .. note:: Correct sub-class implementation:
    * __init__ must include at least one parameter
    * all parameters must have type annotations
    * __init__ must begin with super().__init__()
    """
    @abstractmethod
    def __init__(self):
        subclass_name = type(self).__name__
        self.parameters = signature(type(self)).parameters
        if not self.parameters:
            error_msg = f"No input parameters specified in class {subclass_name}"
            raise ValueError(error_msg)

        if not all((
                isinstance(p.annotation, type)
                and p.annotation != inspect_empty
                for p in self.parameters.values())):
            error_msg = f"Not all input parameters have type annotations in " \
                        f"class {subclass_name}"
            raise TypeError(error_msg)

        super().__init__()

    @abstractmethod
    def analyse(self, save_dir: Path):
        pass


class OddsEvens(Format):
    """Analyse the results of a score in line with the odds and evens format."""
    def __init__(self,
                 penalty_type: str = "points",
                 penalty_per: int = 10):
        super().__init__()

    def odds_evens(self,
                   person_race_result: xml_classes.PersonRaceResult) -> list:
        """
        Evaluate a the control sequence in a :class:`xml_classes.PersonRaceResult`
        for conformance to the odds-and-evens score format (i.e. must visit odd
        controls and even controls each in a block, only switching between once).

        :param person_race_result: :class:`xml_classes.PersonRaceResult` - the
        result to be analysed.
        :return: a list of control codes that did not conform - were found outside
        the first block of their 'type' (odd or even).
        """

        def control_is_odd(control_number):
            return bool(int(control_number) % 2)

        # Extract control_sequence from known PersonRaceResult structure.
        splits_list = person_race_result.SplitTime
        control_sequence = [split.ControlCode for split in splits_list]

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

    def analyse(self, save_dir: Path):
        pass
