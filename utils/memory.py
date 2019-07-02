
class memoize:

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if args not in self.cache:
            self.cache[args] = self.func(self, *args)

        return self.cache[args]

    def clean_cache(self):
        self.cache = {}