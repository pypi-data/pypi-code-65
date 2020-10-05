# Retrieve coverage for the specified file.


def test_coverage():
    client = get_client()
    client.file.get_file_coverage("666", in_wkt=True)
