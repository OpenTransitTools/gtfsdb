def get_test_directory_path():
    """ will return current path ... tries to handle c:\\ windows junk """
    from pkg_resources import resource_filename
    path = resource_filename('gtfsdb', 'tests')
    path = path.replace('c:\\', '/').replace('\\', '/')
    return path
