from setuptools import setup, find_packages 
  
with open('requirements.txt') as f: 
    requirements = f.readlines() 
  
long_description = 'A python based cli to run scripts in a sandbox environment, with docker and gotty' 
  
setup( 
        name ='script-sandbox', 
        version ='1.0.0', 
        author ='Abhishek Kushwaha', 
        author_email ='thecrazycoderabhi@gmail.com', 
        url ='https://github.com/abhishekkushwaha4u', 
        description ='Cli for sanboxing bash and python scripts', 
        long_description = long_description, 
        long_description_content_type ="text/markdown", 
        license ='MIT', 
        packages = find_packages(), 
        entry_points ={ 
            'console_scripts': [ 
                'script-sandbox = scriptAutomation.main:main_operation'
            ] 
        }, 
        classifiers =[ 
            "Programming Language :: Python :: 3", 
            "License :: OSI Approved :: MIT License", 
            "Operating System :: OS Independent", 
        ], 
        keywords ='cli sandbox script python testing abhishekkushwaha4u', 
        install_requires = requirements, 
        zip_safe = False
) 