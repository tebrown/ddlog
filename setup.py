from setuptools import setup

def readme():
      with open('README.rst') as f:
            return f.read()

setup(name='ddlog',
      version='0.2',
      description='Logging handler for sending data to Datadog agent',
      long_description=readme(),
      url='http://github.com/tebrown/ddlog',
      author='Travis Brown',
      author_email='travis@brux.com',
      license='MIT',
      packages=['ddlog'],
      zip_safe=False)
