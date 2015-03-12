
from setuptools import setup

setup(
    name='record',
    version='0.1',
    description=(
        'Easily create lightweight custom record classes'
    ),
    long_description=open('README.rst').read(),
    author='Mark Richards',
    author_email='mark.l.a.richardsREMOVETHIS@gmail.com',
    license='BSD 3-clause',
    py_modules=['record'],
    package_data={'': ['*.rst', '*.txt']},
    classifiers=[
        'Programming Language :: Python',
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)