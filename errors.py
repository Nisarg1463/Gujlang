# Errors file


class Error:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"{self.name} : {self.description}"


class InvalidNumber(Error):
    def __init__(self, description):
        super().__init__("InvalidNumberError", description)


class InvalidCharacter(Error):
    def __init__(self, description):
        super().__init__("InvalidCharacterError", description)
