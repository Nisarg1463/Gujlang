class Position:
    def __init__(self, idx=0, line=1, col=1):
        self.line = line
        self.idx = idx
        self.col = col

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1
        if current_char == "\n":
            self.col = 1
            self.line += 1

    def copy(self):
        return Position(self.idx, self.line, self.col)

    def __repr__(self):
        return f"line {self.line} col {self.col}"
