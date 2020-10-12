from setuptools import setup, find_packages

setup(
    name="todoist_to_markdown",
    version='1.0',
    description='Pythonプロジェクトのテンプレート。主にCLIを作るときに利用する予定',
    author='Kobori Akira',
    author_email='private.beats@gmail.com',
    url='https://github.com/koboriakira/todoist-to-markdown',
    packages=find_packages(),
    entry_points="""
      [console_scripts]
      isttomark = todoist_to_markdown.main:cli
    """,
    install_requires=['python-dotenv',
                      'argparse',
                      'todoist-python'],
)
