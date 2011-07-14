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
      'GeoAlchemy>=0.4.1',
      'SQLAlchemy>=0.6.1',
    ),
    extras_require = {
      'oracle': ['cx_Oracle>=5.0.3'],
      'postgres': ['psycopg2>=2.0.14'],
    },
    entry_points={
      'console_scripts': [
          'gtfsdb-load = gtfsdb.scripts.load:main'
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
