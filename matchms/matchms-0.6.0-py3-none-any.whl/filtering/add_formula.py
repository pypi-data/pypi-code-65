import re
from ..typing import SpectrumType


def add_formula(spectrum_in: SpectrumType) -> SpectrumType:
    """Find formula in InChI or compound name and add to metadata (if not present yet).

    Method to find misplaced formulas in compound name or deduce from InChI.
    """
    if spectrum_in is None:
        return None

    spectrum = spectrum_in.clone()

    formula = spectrum.get("formula", None)

    if spectrum.get("inchi", None) and not formula:
        formula = spectrum.get("inchi").strip().split("/")[1]
        spectrum.set("formula", formula)

    if spectrum.get("compound_name", None) and not formula:
        name = spectrum.get("compound_name", None)
        # Frequently compounds have formula at the end of the name
        if re.search(r"^[C][0-9][0-9A-Z]{4,}$", name.split(" ")[-1]):
            formula = name.split(" ")[-1]
            spectrum.set("formula", formula)

            name_cleaned = " ".join(name.split(" ")[:-1])
            spectrum.set("compound_name", name_cleaned)
            print("Removed formula ({}) from compound name.".format(formula))

    return spectrum
