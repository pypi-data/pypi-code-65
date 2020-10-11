"""
ASFPy methods

Say some things about it here.
"""

from operator import itemgetter
import random
import csv

#################################################
# CONSTANTS
#
# NOTE: These constants refer to data fields that
#	are collected in forms, so may be changed
#	accordingly. The forms should also be
#	preprocesseed to have the same labels.
#
#
#################################################

FLEXIBLE = "flexible"
URM = "urm"
LIM = "lim"
SCHOOL = "du"
NO_CONFLICTS_STATEMENT = "I AM NOT APPLYING TO ANY OF THE FOLLOWING PROFESSORS"

#################################################
# FILE HANDLERS
#################################################

def _id(pre, pad, i, sep = "_"):
    """
    Assign id of string concatenation: `pre + sep + pad + i`, for `i` a 0-padded
    number, i.e., "002".
    """
    return pre + sep + str(i).rjust(pad, "0")

def conflicts(faculty, no_conflict):
    """
    Extract faculty conflict of interest names and create set containing those
    names. First remove the no_conflict statement, if any. Then return faculty.
    """
    faculty = set(faculty.split(", "))
    return {fac for fac in faculty if no_conflict not in fac}

def categories(categories):
    """
    Extract categories from stated categories of respondent.
    """
    return set(categories.split(", "))

def get_element_by_id(_id, group_list):
    """
    Use next generator to find element in a group's list by identifier.
    """
    return next(e for e in group_list if _id == e["id"])

def read_list_csv(filename):
    """
    Use Python's native CSV reader to load list.
    """
    with open(filename) as f:
        loaded = [{k: v for k, v in row.items()}
                for row in csv.DictReader(f, skipinitialspace=True)]
    return loaded

def read_preprocessed_editors_list_csv(filename):
    """
    Use Python's native CSV reader to load the editors list. Also,
    convert category stringlists to sets and endow an identifier.
    """
    editors = read_list_csv(filename)

    n = 1
    for editor in editors:
        editor["id"] = _id("EDI", 3, n)
        editor["categories"] = categories(editor["categories"])
        editor["capacity"] = int(editor["capacity"])
        
        n += 1

    return editors

def read_preprocessed_applicants_list_csv(filename):
    """
    Use Python's native CSV reader to load the applicant submissions list. Also,
    convert category stringlists to sets and endow an identifier.
    """
    applicants = read_list_csv(filename)

    n = 1
    for applicant in applicants:
        applicant["id"] = _id("APP", 3, n)
        applicant["categories"] = categories(applicant["categories"])
        applicant["conflicts"] = conflicts(applicant["conflicts"], NO_CONFLICTS_STATEMENT)
        applicant[FLEXIBLE] = bool(applicant[FLEXIBLE])
        applicant[URM] = bool(applicant[URM])
        applicant[LIM] = bool(applicant[LIM])
        applicant[SCHOOL] = bool(applicant[SCHOOL])

        n += 1

    return applicants

def write_matchings_list_csv(matchings, filename):
    """
    Save dyad-format matchings to CSV list of matchings.
    """
    headers = matchings[0].keys()
    with open(filename, 'w', newline='') as f:
        w = csv.DictWriter(f, headers)
        w.writeheader()
        w.writerows(matchings)

#################################################
# APPLICANT PRIORITY METHODS
#################################################

def asfp_rank(applicant):
    """
    Rank an applicant by attribute combinations by the standard ASFP method of
    ranking by underrepresented minority (URM) status, whether an applicant has
    limited access (LIM) to mentors in academia and research, and if the applicant
    is affiliated with the University of Denver (DU).

    Parameters
    ----------
    applicant: dict
        An object that represents an applicant (often within a list) with 
        attributes including:
            - "id" a unique string identifier
            - "urm" a boolean designation of URM status
            - "lim" a boolean designation of LIM status
            - "du" a boolean designation of DU affiliation

    Returns
    -------
    rank: integer
        A ranking that represents an applicant's pool relative to an
        ASFP-designed schema, as clarified through boolean logic in code below.
    """
    is_urm = applicant[URM]
    is_lim = applicant[LIM]
    is_school = applicant[SCHOOL]

    if (is_urm and is_lim and is_school):
        rank = 0
    elif (is_urm and is_lim):
        rank = 1
    elif (is_urm or is_lim) and is_school:
        rank = 2
    elif (is_urm or is_lim):
        rank = 3
    elif is_school:
        rank = 4
    else:
        rank = 5

    return rank

def randomize(applicants):
    """
    Random permutation of applicant list. Typical usage is before
    prioritization.
    """
    return random.sample(applicants, k = len(applicants))

def prioritize(applicants, rank_method = asfp_rank):
    """
    Prioritize applicants by rank of attributes. Applicants are randomized
    prior to running the ranking and sorting.

    Parameters
    ----------
    applicants: list
        The list `applicants` of dicts of each applicant.
    rank_method: function
        The method of assinging ranks under label "rank" based on attributes
        that are necessarily present in items of `applicants`.

    Returns
    -------
    applicants: list
        A copy of applicants is returned, sorted by rank as determined by
        `rank_method`.
    """
    for a in applicants:
        a["rank"] = rank_method(a)

    return sorted(applicants, key = itemgetter("rank"))

#################################################
# EDITOR-ONLY METHODS
#################################################

def editors_by_role(editors, role):
    """
    Get a sublist of editors by role.
    """
    return [e for e in editors if e["role"] == role]

def editors_by_categories(editors, categories):
    """
    Get a sublist of editors by category
    """
    return [e for e in editors if e["categories"].intersection(categories)]

def capacity(editors):
    """
    Compute editing capacity, the number of statements an editor
    can read, for a list of editors.
    """
    return sum(e["capacity"] for e in editors)


def find_highest_capacity_category(applicant, editors):
    """
    Find the highest capacity category based on editors'
    availability given stated category preferences of an applicant.

    Parameters
    ----------
    applicant: dict
        The dict object representing an applicant that has categories
        in a set.
    editors: list
        The editors list of dicts is some subset of editors.

    Returns
    -------
    Returns the highest capacity category given applicant category preferences
    as listed in the set.
    """
    
    capacities = [{
        "capacity": capacity(editors_by_categories(editors, {category})),
        "category": category
    } for category in applicant["categories"]]

    sorted_capacities = sorted(capacities, 
                               key = itemgetter("capacity"), 
                               reverse = True)

    return sorted_capacities[0]["category"]

def find_match(applicant, editors):
    """
    Match an applicant to editors, if possible.
    """
    if capacity(editors) > 0:
    # If at least one editor in a list is available for an applicant,
    # find the best possible match and assign.

        highest_capacity_category = find_highest_capacity_category(applicant, editors)

        highest_capacity_editors = sorted(
            editors_by_categories(editors, {highest_capacity_category}),
            key = itemgetter("capacity"),
            reverse = True
        )

        editor_id = highest_capacity_editors[0]["id"]

        return highest_capacity_editors[0]["id"]

    else:
    # If no editors have capacity within the group, return None
        return None

def update_capacity(editor_id, editors):
    """
    Update capacity of editor within a list by id.
    """
    for editor in editors:
        if editor["id"] == editor_id:
            editor["capacity"] -= 1

def remove_conflicts(applicant, potential_editors):
    """
    Remove editors from potential editors who might be sources of conflict of
    interest. These are typically by name, and not be assigned ASFPy _id
    generator.
    """
    return [editor for editor in potential_editors if
                editor["name"] not in applicant["conflicts"]]

def find_potential_editors(applicant, editors):
    """
    Find potential editors given applicant categories and conflicts.
    """
    category_editors = editors_by_categories(editors, applicant["categories"])
    return remove_conflicts(applicant, category_editors)

def allocate(applicants, editors):
    """
    Allocate applicants to editors.
    """
    unmatched = [applicant["id"] for applicant in applicants]
    matchings = []

    for applicant in applicants:

        potential_editors = find_potential_editors(applicant, editors)

        if capacity(potential_editors) < 2:
        # If the editing capacity for an applicant is less than 2, continue to next applicant
            continue
        else:

            _match = {
                "applicant": applicant["id"],
                "editors": []
            }

            faculty_editors = editors_by_role(potential_editors, "faculty")
            student_editors = editors_by_role(potential_editors, "student")

            faculty_editor_match = find_match(applicant, faculty_editors)

            if (faculty_editor_match is not None) and (capacity(student_editors) > 0):
            # If a faculty editor match is possible and at least one student editor
            # match is possible, then add a faculty editor match and update capacity.
                _match["editors"].append(faculty_editor_match)
                update_capacity(faculty_editor_match, faculty_editors)
            else:
                if capacity(student_editors) < 2:
                # If fewer than 2 student editors are available, skip to next
                # applicant.
                    continue
                elif applicant[FLEXIBLE]:
                # If an applicant is flexible and prefers to be matched with two
                # student editors, find first match here.
                    student_editor_match = find_match(applicant, student_editors)
                    if student_editor_match is not None:
                        _match["editors"].append(student_editor_match)
                        update_capacity(student_editor_match, student_editors)
                else:
                # If applicant prefers not to have a match if at least one faculty
                # editor is not available, then continue to next applicant.
                    continue

            # Add a second editor: A student editor match. Then update
            # capacity of that editor.
            student_editor_match = find_match(applicant, student_editors)
            _match["editors"].append(student_editor_match)
            update_capacity(student_editor_match, student_editors)

            # Append the match to matchings and remove this applicant
            # from the list of unmatched applicants.
            matchings.append(_match)
            unmatched.remove(applicant["id"])

    return {
        "matchings": matchings,
        "unmatched": unmatched,
        "editors": editors
    }


def format_matchings(matchings, applicants, editors):
    """
    Create dyadic format matchings, returning list of dicts with
    pairings of editors and applicants, including categories and
    statements with notes from applicants.

    NOTE: The applicants and editors list args expect the original lists with
        detailed information, not just the output of allocate.
    """
    dyads = []
    for matching in matchings:
        # Get applicant id from match and then get applicant details
        # from applicants list
        applicant_id = matching["applicant"]
        applicant = get_element_by_id(applicant_id, applicants)

        # Get editor ids and then get both detailed editor elements from list
        editor_ids = matching["editors"]
        for editor_id in editor_ids:
            editor = get_element_by_id(editor_id, editors)

            dyads.append({
                "editor_id": editor["id"],
                "editor_email": editor["email"],
                "editor_name": editor["name"],
                "editor_categories": ", ".join(str(c) for c in editor["categories"]),
                "applicant_id": applicant["id"],
                "applicant_name": applicant["name"],
                "applicant_email": applicant["email"],
                "applicant_statement": applicant["statement"],
                "applicant_notes": applicant["notes"],
                "applicant_categories": ", ".join(str(c) for c in applicant["categories"]),
            })
            
    return dyads
    
def compile_unmatched_applicants(unmatched, applicants):
    """
    Compile list of unmatched applicants after allocation.

    NOTE: unmatched is a list of applicant IDs and applicants in the official
        list of applicants
    """
    return [a for a in applicants if a["id"] in unmatched]
