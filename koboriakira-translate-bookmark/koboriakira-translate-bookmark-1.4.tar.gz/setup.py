from setuptools import setup, find_packages

setup(
    name="koboriakira-translate-bookmark",
    version='1.4',
    description='自分がよくみるサイトの翻訳手助けツール',
    author='Kobori Akira',
    author_email='private.beats@gmail.com',
    url='https://github.com/koboriakira/koboriakira-translate-bookmark',
    packages=find_packages(),
    entry_points="""
      [console_scripts]
      translate = translate_bookmark.main:cli
    """,
    install_requires=['bs4',
                      'requests',
                      'googletrans'
                      ],
)
