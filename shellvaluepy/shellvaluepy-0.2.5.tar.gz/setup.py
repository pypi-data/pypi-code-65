from setuptools import setup
lond_d = '''
```
pip3 install shellvaluepy
```

```py
#input
from shellvaluepy.info import shell

shell.value('dir')

#output
XXXXX XX XXXX
XXX X XXXXXXXXXXX X X
```

```py
#input
from shellvaluepy.info import shell

shell.install('shell_value')

#output
OK to install!
or
error!
```
'''
setup(name="shellvaluepy",
      version="0.2.5",
      url="https://github.com/hminkoo10/shell_value",
      license="MIT",
      author="hminkoo10",
      author_email="hmin.koo10@gmail.com",
      long_description=lond_d,
      long_description_content_type="text/markdown",
      description="made by hminkoo10, discord : Crewmate#7777, email: hmin.koo10@gmail.com",
      packages=['shellvaluepy'],
      install_requires=['subprocess']
      )
      
