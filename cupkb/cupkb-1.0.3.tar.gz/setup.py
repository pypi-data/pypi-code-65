from setuptools import find_packages,setup


setup(name='cupkb',version='1.0.3',description="text2sql",
      #packages=["ckpt","conceptNet","data","preprocess","saved_model","src"],
      packages=find_packages(),
      py_modules=["train"],
      data_files=["well_data_1.xls","bert/modeling.py","bert/convert_tf_checkpoint_to_pytorch.py","bert/tokenization.py",
                  "sqlnet/dbengine.py","wikisql/annotate.py","wikisql/evaluate.py","wikisql/lib/common.py","wikisql/lib/dbengine.py","wikisql/lib/query.py","wikisql/lib/table.py"],
      install_requires=['record','torch==1.6.0'])