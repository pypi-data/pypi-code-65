import pytest

from .controls import ToggleControl
from .section import Section, SectionGroup

def test_duplicate_control_property():
    section_with_duplicates = (
        Section('Section with duplicates')
        .append(ToggleControl("trainer.use_float16", "foo", default_value=False))
        .append(ToggleControl("trainer.use_float16", "foo", default_value=False)))
    sg = SectionGroup()

    with pytest.raises(Exception) as excinfo:
        sg.append(section_with_duplicates)
    assert "Property already exists" in str(excinfo.value)

    section_without_duplicates = (
        Section('Section')
        .append(ToggleControl("trainer.use_float16", "foo", default_value=False)))
    sg = SectionGroup()
    sg.append(section_without_duplicates)

    with pytest.raises(Exception) as excinfo:
        sg.append(section_without_duplicates)
    assert "Property already exists" in str(excinfo.value)
