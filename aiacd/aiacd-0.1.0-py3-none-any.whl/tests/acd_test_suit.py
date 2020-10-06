import pytest
import os


@pytest.fixture
def rls_to_acd_init():
    rls_to_acd_path = os.getcwd()
    rls_to_acd_out_path = os.getcwd()

    return [rls_to_acd_path, rls_to_acd_out_path]


@pytest.mark.rls_to_acd
def test_generate_used_techniques_from_raw(rls_to_acd_init):
    import os
    from aiacd.rls_to_acd_transform import generate_used_techniques_from_raw
    import re

    root_path = rls_to_acd_init[0]
    tech_dict = {"O": "OptDigMicr", "E": "EDS", "F": "FTIR", "S": "SEM"}
    folders = [os.path.join(root_path, folder) for folder in os.listdir(root_path)]
    for sub_folders in folders:
        test_return = generate_used_techniques_from_raw(sub_folders)
        test_return_search = re.findall(r"(?:OptDigMicr|EDS|FTIR|SEM)", test_return)
        test_return_validate = set()
        for group in test_return_search:
            test_return_validate.add(group)
        code = str(sub_folders.split("_")[-1])
        code_set = set()
        for sub_code in code:
            code_set.add(tech_dict.get(sub_code))
        assert set(test_return_validate) == code_set


@pytest.mark.rls_to_acd
def test_acd_convert(rls_to_acd_init):
    import os
    import shutil
    import json

    source_root = rls_to_acd_init[0]
    source_folders = os.listdir(rls_to_acd_init[0])
    source_path_list = [os.path.join(source_root, folder) for folder in source_folders]
    output_path = rls_to_acd_init[1]
    from aiacd.rls_to_acd_transform import acd_convert

    for source_path, out_folder in zip(source_path_list, source_folders):
        temp_output = os.path.join(output_path, out_folder)
        acd_convert(source_path, temp_output)
        t_dict = {}
        for root, dirs, files in os.walk(temp_output, topdown=True):
            t_dict[root] = [dirs, files]

        with open("{}.json".format(temp_output)) as data_file:
            data_loaded = json.load(data_file)
            assert data_loaded == t_dict
            shutil.rmtree(temp_output)
