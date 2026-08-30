class NotFoundError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
        self.code = 404

    def __str__(self):
        return f"{self.message}"