
from setuptools import setup

setup(
    name='reck',
    version='0.1',
    description=(
        'Easily create lightweight, mutable record classes'
    ),
    long_description=open('README.rst').read(),
    author='Mark Richards',
    author_email='mark.l.a.richardsREMOVETHIS@gmail.com',
    license='BSD 3-Clause',
    packages=['reck'],
    test_suite='tests',
    package_data={'': ['*.rst', '*.txt']},
    classifiers=[
        'Programming Language :: Python',
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
