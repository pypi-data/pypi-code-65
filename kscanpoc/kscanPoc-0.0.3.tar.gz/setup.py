from distutils.core import setup
import setuptools
setup(
	name='kscanPoc',  # 包的名字
	version='0.0.3',  # 版本号
	description='kscan kscanpocs',  # 描述
	author='wanqian1',  # 作者
	author_email='wanqian1@kingsoft.com',  # 你的邮箱**
	url='',  # 可以写github上的地址，或者其他地址,
	maintainer='chenyang7',
	maintainer_email='chengyang7@kingsoft.com',
	include_package_data=True,
	packages=setuptools.find_packages(exclude=['test', 'examples', 'script', 'tutorials']),  # 包内需要引用的文件夹

	# 依赖包
	install_requires=[
		'requests',
		'pymongo',
		'pymysql',
		'psycopg2-binary',
		'redis',
	],
	zip_safe=True,
)