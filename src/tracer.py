import sys

class Tracer(object):
    def __init__(self, method):
        self.method = method
    def __enter__(self):
        sys.settrace(self.method)
    def __exit__(self, type, value, traceback):
        sys.settrace(None)
