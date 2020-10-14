from pathlib import Path

from filesystemlib import walk


def test_walk():
    project_dir = Path(__file__).parent.parent
    project_paths = set(map(Path, walk(project_dir)))
    assert project_paths >= {
        project_dir / "setup.py",
        project_dir / "filesystemlib" / "__init__.py",
        project_dir / "filesystemlib" / "walk.py",
    }
