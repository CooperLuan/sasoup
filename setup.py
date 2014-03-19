# coding: utf-8
from setuptools import setup, find_packages

AUTHOR = 'Cooper'
AUTHOR_EMAIL = 'lannikcooper@gmail.com'
PACKAGE = 'sasoup'
NAME = 'sasoup'
DESCRIPTION = 'sasoup'
VERSION = __import__(PACKAGE).__version__


setup(name='sasoup',
      version=VERSION,
      description='html parser base on rules',
      long_description="""\
ryan""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
      ],
      keywords='sasoup',
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sasoup'],
      include_package_data=True,
      test_suite='nose.collector',
      test_requires=['Nose'],
      zip_safe=True,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
