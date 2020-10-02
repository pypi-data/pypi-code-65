import json
import os.path as osp


def load_json(file_path):
    """Load json function.

    Parameters
    ----------
    file_path : str or pathlib.PosixPath
        json file path

    Returns
    -------
    data : dict
        loaded json data
    """
    if not osp.exists(str(file_path)):
        raise OSError('{} not exists'.format(str(file_path)))
    with open(str(file_path), "r") as f:
        return json.load(f)


def save_json(data, filename,
              save_pretty=True,
              sort_keys=True,
              ensure_ascii=True):
    """Save json function.

    Parameters
    ----------
    data : dict
        save data
    filename : str
        save path
    """
    filename = str(filename)
    with open(filename, "w") as f:
        if save_pretty:
            f.write(json.dumps(data, indent=4,
                               ensure_ascii=ensure_ascii,
                               sort_keys=sort_keys,
                               separators=(',', ': ')))
        else:
            json.dump(data, f)
        f.write('\n')
