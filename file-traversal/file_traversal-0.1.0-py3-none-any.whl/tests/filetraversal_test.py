import os
from filetraversal import FileTraversal

test_path = os.path.join(os.getcwd(), 'tests', 'mock_directory')

def mock_file(item):
    assert item is not None

def mock_folder(item):
    assert item is not None

def test_recurse_noargs():
    file_traversal = FileTraversal()
    result = file_traversal.recurse(test_path)
    folders_traversed = result.getfolderstraversed()
    files_traversed = result.getfilestraversed()
    assert len(folders_traversed) == 2
    assert len(files_traversed) == 1
    assert isinstance(folders_traversed[0], str)
    assert isinstance(folders_traversed[1], list)
    assert isinstance(files_traversed[0], list)
    assert result.getmaximumdepth() == 4
    
def test_recurse():
    file_traversal = FileTraversal(foldermethod=mock_folder, filemethod=mock_file)
    result = file_traversal.recurse(test_path)
    folders_traversed = result.getfolderstraversed()
    files_traversed = result.getfilestraversed()
    assert len(folders_traversed) == 2
    assert len(files_traversed) == 1
    assert isinstance(folders_traversed[0], str)
    assert isinstance(folders_traversed[1], list)
    assert isinstance(files_traversed[0], list)
    assert result.getmaximumdepth() == 4