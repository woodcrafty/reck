
from setuptools import setup, find_packages

#import record

setup(
    name='record',
    #version=record.__version__,
    version='0.1.0',
    description=(
        'Similar to namedtuple, but field values are mutable and there is no '
        'limit on the number of fields'
    ),
    long_description=open('README.rst').read(),
    author='Mark Richards',
    author_email='mark.l.a.richardsREMOVETHIS@gmail.com',
    license='BSD 3-clause',
    #packages=find_packages(),
    #packages=['record'],
    py_modules=['record', 'test_record'],
    package_data={'': ['*.rst', '*.txt']},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)