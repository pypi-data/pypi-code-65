from distutils.core import setup
setup(
  name = 'higradpy',         # How you named your package folder (MyLib)
  packages = ['higradpy'],   # Chose the same as "name"
  version = '0.15',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Python Implementation of Hierarchical Incremental Gradient Descent',   # Give a short description about your library
  long_description="""This is the Python package for HiGrad (Hierarchical Incremental Gradient Descent), an algorithm for statistical inference for online learning and stochastic approximation.

Stochastic gradient descent (SGD) is an immensely popular approach for online learning in settings where data arrives in a stream or data sizes are very large. However, despite an ever-increasing volume of work on SGD, much less is known about the statistical inferential properties of SGD-based predictions. Taking a fully inferential viewpoint, this paper introduces a novel procedure termed HiGrad to conduct statistical inference for online learning, without incurring additional computational cost compared with the vanilla SGD. The HiGrad procedure begins by performing SGD iterations for a while and then split the single thread into a few, and this procedure hierarchically operates in this fashion along each thread. With predictions provided by multiple threads in place, a t-based confidence interval is constructed by decorrelating predictions using covariance structures given by the Ruppert–Polyak averaging scheme. Under certain regularity conditions, the HiGrad confidence interval is shown to attain asymptotically exact coverage probability.

Reference: Weijie Su and Yuancheng Zhu. (2018) Statistical Inference for Online Learning and Stochastic Approximation via Hierarchical Incremental Gradient Descent.
""",
  long_description_content_type="text/markdown",
  author = 'Vihan Singh',                   # Type in your name
  author_email = 'vihan13singh@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/user/vihan13singh',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/vihan13singh/higradpy/archive/0.1.tar.gz',    # I explain this later on
  keywords = ['Statistical Inference', 'Machine Learning', 'Stochastic Gradient Descent'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
          'numpy',
          'matplotlib',
          'scikit-learn',
          'scipy',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)