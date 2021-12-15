from setuptools import setup

setup(
    name='guru',
    version='1.0.0',
    packages=['guru'],
    entry_points={
        'console_scripts': [
            'guru = guru.__main__:main'
        ]
    })
