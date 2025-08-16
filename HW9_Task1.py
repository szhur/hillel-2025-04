GLOBAL_CONFIG = {"feature_a": True, "max_retries": 3}

class Configuration:
    def __init__(self, updates, validator=None):
        self.updates = updates or {}
        self.validator = validator
        self._original = None

    def __enter__(self):
        global GLOBAL_CONFIG
        # Save a copy of the current configuration
        self._original = GLOBAL_CONFIG.copy()

        # Apply updates
        new_config = GLOBAL_CONFIG.copy()
        new_config.update(self.updates)

        # Validate if a validator is provided
        if self.validator and not self.validator(new_config):
            raise ValueError("Invalid configuration")

        GLOBAL_CONFIG = new_config
        return GLOBAL_CONFIG

    def __exit__(self, exc_type, exc_value, traceback):
        global GLOBAL_CONFIG
        # Always restore the original configuration
        GLOBAL_CONFIG = self._original
        # Do not suppress exceptions
        return False


def validate_config(config):
    # Ensure max_retries >= 0
    return config.get("max_retries", 0) >= 0


# Example usage
print("Before:", GLOBAL_CONFIG)

try:
    with Configuration({"max_retries": 5}, validator=validate_config):
        print("Inside valid context:", GLOBAL_CONFIG)
        # Raise an error to test rollback
        raise RuntimeError("Something went wrong")
except RuntimeError:
    print("Caught an error, but config restored.")

print("After:", GLOBAL_CONFIG)