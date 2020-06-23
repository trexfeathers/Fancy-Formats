import pathlib
import pytest

from fancy_formats import process_results


class TestFormat:
    def test_abstract_init(self):
        class FormatSubClass(process_results.Format):
            pass

        with pytest.raises(TypeError, match=r"Can't instantiate .*__init__"):
            FormatSubClass()

    def test_abstract_analyse(self):
        class FormatSubClass(process_results.Format):
            def __init__(self):
                super().__init__()

        with pytest.raises(TypeError, match=r"Can't instantiate .*analyse"):
            FormatSubClass()

    def test_need_params(self):
        class FormatSubClass(process_results.Format):
            def __init__(self):
                super().__init__()

            def analyse(self):
                pass

        with pytest.raises(ValueError, match=r"No input parameters .*"):
            FormatSubClass()