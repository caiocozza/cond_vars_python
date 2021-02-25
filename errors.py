class KeyExistsRegistrationException(Exception):
    def __init__(self, key: str):
        self.message = f"Cannot recreate a valid key '{key}'"
        super().__init__(self.message)

class KeyNotFound(Exception):
    def __init__(self, key: str):
        self.message = f"Key '{key}' cannot be found"
        super().__init__(self.message)