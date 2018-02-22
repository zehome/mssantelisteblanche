# -*- coding: utf-8 -*-

from setuptools import setup
setup(
    name="mssantelisteblanche",
    entry_points={
        'console_scripts': [
            'mssante_listeblanche = mssantelisteblanche.main:main'
        ]
    }
)
