def get_test_directory_path():
    """ will return current path ... tries to handle c:\\ windows junk """
    from pkg_resources import resource_filename
    path = resource_filename('gtfsdb', 'tests')
    path = path.replace('c:\\', '/').replace('\\', '/')
    return path


def get_test_file_uri(test_file):
    """ will send back proper file:////blah/test_file.zip """
    import os
    dir_path = get_test_directory_path()
    file_path = "file://{0}".format(os.path.join(dir_path, test_file))
    file_path = file_path.replace('\\', '/')
    return file_path

def get_temp_sqlite_db_url():
    import tempfile
    import logging
    log = logging.getLogger(__name__)

    db_file = tempfile.mkstemp()[1]
    url = 'sqlite:///{0}'.format(db_file)
    log.debug("DATABASE TMP FILE: {0}".format(db_file))
    return url
