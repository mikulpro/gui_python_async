class SingletonClass:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonClass, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize the instance attributes here (if needed)
        pass

# Usage example
singleton_instance1 = SingletonClass()
singleton_instance2 = SingletonClass()

print(singleton_instance1 is singleton_instance2)  # Output will be True