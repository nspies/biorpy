from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='biorpy',
      version='0.9.2',
      description='Wrapper for RPy2 featuring default arguments, auto conversion to/from numpy and pandas',
      long_description=readme(),
      url='https://bitbucket.org/nspies/biorpy',
      author='Noah Spies',
      license='MIT',
      packages=['biorpy'],
      install_requires=[
          'numpy',
          'pandas',
          'rpy2'
      ],
      zip_safe=False)
