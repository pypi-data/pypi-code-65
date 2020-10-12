import json

def export_metadata_as_json(spectrums, filename, include_fields="all"):
    """Export metadata to json file.
    
    Parameters
    ----------
    spectrum_in: SpectrumType
        Input spectrum.
    include_fields: list or "all"
        Specify which metadata field should be exported. When set to "all", all
        metadata will be exported to json file. Alternatively, pass list of desired
        field names, e.g. "include_fields=['spectrumid', 'smiles', 'inchi' ....]".
    """
    def get_metadata_dict(include_fields):
        if include_fields == "all":
            return spec.metadata
        if not isinstance(include_fields, list):
            print("'Include_fields' must be 'all' or list of keys.")
            return None

        return {key: spec.metadata[key] for key in spec.metadata.keys()
                & include_fields}

    metadata_dicts = []
    for spec in spectrums:
        metadata_dict = get_metadata_dict(include_fields)
        if metadata_dict:
            metadata_dicts.append(metadata_dict)

    with open(filename, 'w') as fout:
        json.dump(metadata_dicts, fout)
