__author__ = 'rhunter'
import requests
import concurrent.futures


class BadResponse(Exception):
    pass


def get_json_url(url):
    resp = requests.get(url)
    if resp.status_code != 200:
        raise BadResponse
    return resp.json()


def get_url(url):
    return get_json_url(url)['data']


class Concurrency(object):
    def __init__(self, max_workers=10):
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def submit(self, *args):
        self.futures.append(self.pool.submit(*args))

    def bulk_apply(self, function_handle, arg_list):
        for v in arg_list:
            self.submit(function_handle, v)
        return self.wait()

    def wait(self):
        f_list = [f.result() for f in self.futures]
        self.futures[:]=[]
        return f_list
