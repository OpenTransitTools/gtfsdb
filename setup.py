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
        'GeoAlchemy>=0.1',
        'SQLAlchemy>=0.5.8,<=0.5.999',
      ),
      extras_require = {
        'oracle': ['cx_Oracle>=5.0.3'],
        'postgres': ['psycopg2>=2.0.14'],
      },
      entry_points={
        'console_scripts': [
            'gtfsdb-load = gtfsdb.scripts.load:main'
        ]
      }
)
