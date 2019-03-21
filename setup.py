from setuptools import setup, find_packages
import sys


oracle_extras = ['cx_oracle>=5.1']
postgresql_extras = ['psycopg2>=2.4.2']
# dev_extras = oracle_extras + postgresql_extras
dev_extras = []

extras_require = dict(
    dev=dev_extras,
    oracle=oracle_extras,
    postgresql=postgresql_extras,
)

install_requires = [
    'geoalchemy2',
    'sqlalchemy',
    'psycopg2',
]

setup(
    name='gtfsdb',
    version='0.5.0',
    description='GTFS Database',
    long_description=open('README.rst').read(),
    keywords='GTFS',
    author="Open Transit Tools",
    author_email="info@opentransittools.org",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'gtfsdb-load = gtfsdb.scripts:gtfsdb_load',
            'gtfsdb-current-load = gtfsdb.scripts:current_tables_cmdline',
            'rs-test = gtfsdb.scripts:route_stop_load',
            'connect-tester = gtfsdb.scripts:db_connect_tester',
        ]
    },
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
    ),
)
