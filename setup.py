from setuptools import setup, find_packages

version = '0.1dev'

setup(name='gtfsdb',
      version=version,
      description="GTFS Database",
      keywords='GTFS',
      author='Mike Gilligan',
      author_email='gilligam@trimet.org',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=(
        'GeoAlchemy',
        'SQLAlchemy >= 0.5',
      ),
      extras_require = {
        'oracle': ['cx_Oracle'],
        'postgres': ['psycopg2'],
      },
      entry_points={
        'console_scripts': [
            'gtfsdb-load = gtfsdb.scripts.load:main'
        ]
      }
)
