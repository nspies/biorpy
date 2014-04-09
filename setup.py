from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='biorpy',
      version='0.9.1',
      description='Wrapper for RPy2 featuring default arguments, auto conversion to/from numpy and pandas',
      long_description=readme(),
      url='https://bitbucket.org/nspies/biorpy',
      author='Noah Spies',
      author_email='nsies@gmail.vom',
      license='MIT',
      packages=['biorpy'],
      install_requires=[
          'numpy',
          'pandas',
          'rpy2'
      ],
      zip_safe=False)