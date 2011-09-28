from setuptools import setup, find_packages

version = '0.1dev'

setup(
    name='gtfsdb',
    version=version,
    description='GTFS Database',
    long_description=open('README').read(),
    keywords='GTFS',
    author='Mike Gilligan',
    author_email='gilligam@trimet.org',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=(
      'argparse>=1.2.1',
      'GeoAlchemy>=0.6',
      'SQLAlchemy>=0.7.2',
      'transitfeed>=1.2.7',
    ),
    extras_require = {
      'oracle': ['cx_Oracle>=5.1'],
      'postgresql': ['psycopg2>=2.4.2'],
    },
    entry_points={
      'console_scripts': [
          'gtfsdb-load = gtfsdb.scripts.load:main',
          'gtfsdb-validate = gtfsdb.scripts.validate:main'
      ]
    },
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
