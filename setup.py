from setuptools import setup
from setuptools import find_packages

setup(
    name='mudpie',
    version='0.1.0',
    packages=find_packages(),
    package_data={
        'mudpie': [
            '.data/*.json',
        ],
    },
    extras_require={
        'test': [
            'pytest',
        ],
    },
)
