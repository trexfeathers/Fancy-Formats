import pathlib
import pytest

from fancy_formats import process_results


class TestFormat:
    def test_need_vars(self):
        class FormatSubClass(process_results.Format):
            def __init__(self):
                super().__init__()

            def analyse(self):
                pass

        with pytest.raises(ValueError, match=r"No input arguments.*"):
            FormatSubClass()

    def test_abstract_analyse(self):
        class FormatSubClass(process_results.Format):
            def __init__(self):
                super().__init__()

        with pytest.raises(TypeError, match=r"Can't instantiate.*"):
            FormatSubClass()
