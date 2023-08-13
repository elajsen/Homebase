


class Singleton:
    _instances = {}
    _instance = None

    def __new__(cls, *args, **kwargs):
        if args[0] not in cls._instances.keys():
            cls._instances[args[0]] = super().__new__(cls)
        return cls._instances[args[0]]

    @classmethod
    def clear_cache(cls):
        cls._instances.clear()