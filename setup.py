from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

exec(open('dmstudio/version.py').read())

version = __version__


setup(name='dmstudio',
      version=version,
      description='Python module for Datamine Studio scripting',
      url='https://github.com/seanhoran/dmstudio',
      download_url='https://github.com/seanhoran/dmstudio/archive/0.0.1-beta.tar.gz',
      author='Sean Horan',
      author_email='sean.horan@rpacan.com',
      license='MIT',
      include_package_data=True,
      package_data={'':['LICENCES.txt'], '':['README.md']},
      packages=find_packages(),
      zip_safe=False)
