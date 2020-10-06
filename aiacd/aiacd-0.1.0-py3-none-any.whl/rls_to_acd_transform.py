import os
import re

from .tools import log, log_factory, make_directory_and_copy_files, walk
from .re_tools import re_extract, re_extract_try, re_find_all, re_search_strings

debug_logger = log_factory("debug", "File_Structure_Error")


def date_lims_test_freetext_rename(input_path):
    """Converts from LIMS_Test_Date_Freetext to:
    Date_LIMS_Test_Freetext
    if data conforms will never do anything visible
    Usage should probably be avoided in most cases debugging this function
    for all possible issues would be a lot of maintenance

    """
    m_search_strings = re_search_strings()
    used_techniques_hashable = generate_used_techniques_from_raw(input_path)
    for (
        current_path,
        dir_in_cur_path,
        files_in_cur_path,
    ) in os.walk(input_path):
        if re.search(used_techniques_hashable, current_path) is not None:
            for file in files_in_cur_path:
                b_check1 = re_extract_try(
                    file, m_search_strings["search_string_spectrum_word"]
                )
                b_check2 = re_extract_try(
                    file, m_search_strings["search_string_spectrum_csv"]
                )
                if not (b_check1 or b_check2):
                    m_free_text = re_extract_try(
                        file, m_search_strings["search_string_free_text"], 0
                    )
                    temp_m_lims = re_find_all(
                        file, m_search_strings["seach_string_LIMS_in_files_Future"]
                    )
                    # This implies the date is messed up
                    if len(temp_m_lims) > 1:
                        m_lims = temp_m_lims[1]
                    elif len(temp_m_lims) == 1:
                        m_lims = temp_m_lims[0]
                    else:
                        m_lims = None
                    m_date = re_extract_try(
                        file, m_search_strings["search_string_date"], 0
                    )
                    if m_date is None:
                        import datetime

                        temp_path = os.path.join(current_path, file)
                        m_date = (
                            datetime.datetime.fromtimestamp(os.path.getmtime(temp_path))
                            .date()
                            .isoformat()
                            .replace("-", "")
                        )
                    m_test = re_extract_try(
                        file, m_search_strings["search_string_test"], 0
                    )
                    m_name = "_".join(
                        list(
                            filter(
                                lambda x: x is not None,
                                [m_date, m_lims, m_test, m_free_text],
                            )
                        )
                    )
                    if m_name != file:
                        log(debug_logger, (m_name, file))
                    try:
                        os.rename(
                            os.path.join(current_path, file),
                            os.path.join(current_path, m_name),
                        )
                    except:
                        log(
                            debug_logger,
                            "Folder already exists: {} => {}".format(
                                os.path.join(current_path, file),
                                os.path.join(current_path, m_name),
                            ),
                        )
                        continue


def generate_used_techniques_from_raw(input_path):
    used_techniques = set()
    techniques = {"FTIR", "SEM", "EDS", "OptDigMicr", "mFTIR"}
    bad_optical = {r"(OptDig)(.+)?(?=_)", r"(Optic)(.+)?(?=_)"}
    for (
        current_path,
        dir_in_cur_path,
        files_in_cur_path,
    ) in os.walk(input_path):
        for directory in dir_in_cur_path:
            used_techniques.update([data for data in re_extract(directory, techniques)])
            bad_tech = [data for data in re_extract(directory, bad_optical)]
            for bad in bad_tech:
                # TODO: Refactor this side effect
                temp = directory.replace(
                    re.search(bad, directory).group(0), "OptDigMicr"
                )
                new_directory = os.path.join(input_path, temp)
                old_directory = os.path.join(input_path, directory)
                used_techniques.add("OptDigMicr")
                try:
                    os.rename(old_directory, new_directory)
                except FileNotFoundError:
                    log(
                        debug_logger,
                        "Failure of: {} ---> {}".format(old_directory, new_directory),
                    )
            pass
    return "(?:{})".format("|".join(used_techniques))


def acd_convert(input_path, output_path):
    m_log = set()
    m_file_list = set()
    m_search_strings = re_search_strings()
    used_techniques_hashable = generate_used_techniques_from_raw(input_path)
    print("Converting : {}".format(input_path))
    for current_directory, subfolders, file in os.walk(input_path):
        if used_techniques_hashable is not None:
            if re_extract_try(
                current_directory, m_search_strings["search_string_RLS_directory"], 1
            ):
                for f in file:
                    if re.search(used_techniques_hashable, current_directory):
                        m_file_list.add(f)
                        tech = re.search(
                            used_techniques_hashable, current_directory
                        ).group()
                        if re_extract_try(
                            f, m_search_strings["seach_string_LIMS_in_files_Future"], 0
                        ):
                            lims = re_extract_try(
                                f,
                                m_search_strings["seach_string_LIMS_in_files_Future"],
                                0,
                            )
                            if lims is not None:
                                m_log.add(f)
                                make_directory_and_copy_files(
                                    f, current_directory, output_path, lims, tech
                                )

    for current_directory, _, file in walk(input_path, 2):
        for f in file:
            if re_extract_try(f, m_search_strings["search_string_results_form"]):
                make_directory_and_copy_files(f, current_directory, output_path)
            if re_extract_try(f, m_search_strings["search_string_doc_file"]):
                make_directory_and_copy_files(f, current_directory, output_path)

    if re.search("EDS", used_techniques_hashable):
        for current_directory, _, file in walk(input_path, 3):
            for f in file:
                b_check1 = re_extract_try(
                    f, m_search_strings["search_string_spectrum_word"]
                )
                b_check2 = re_extract_try(
                    f, m_search_strings["search_string_spectrum_csv"]
                )
                if b_check1:
                    make_directory_and_copy_files(f, current_directory, output_path)
                if b_check2:
                    make_directory_and_copy_files(f, current_directory, output_path)

    missed_data = list(m_log ^ m_file_list)
    if missed_data is not None:
        log(debug_logger, "Missed Data For Project << {} >>".format(output_path))
        for missed in missed_data:
            log(debug_logger, "Missed data: {}".format(missed))
        log(
            debug_logger,
            "---------------------------------------------------------------",
        )
