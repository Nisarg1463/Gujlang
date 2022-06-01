from errors import *
from position import Position
import json

# tokenizing file

digits = "0123456789"
chars = "abcdefghijklmnopqrstuvwxyz_"

# token


tt_int = "TT_INT"
tt_double = "TT_DOUBLE"
tt_mul = "TT_MUL"
tt_div = "TT_DIV"
tt_sub = "TT_SUB"
tt_add = "TT_ADD"
tt_lparam = "TT_LPARAM"
tt_rparam = "TT_RPARAM"
tt_keyword = "TT_KEYWORD"
tt_identifier = "TT_IDENTIFIER"
tt_escape_sequence = "TT_ESCAPE_SEQUENCE"
tt_true = "TT_TRUE"
tt_false = "TT_FALSE"
tt_string = "TT_STRING"
tt_fstring = "TT_FSTRING"
tt_indent = "TT_INDENT"
tt_new_line = "TT_NEW_LINE"
tt_comment = "TT_COMMENT"
tt_list_start = "TT_LIST_START"
tt_list_end = "TT_LIST_END"
tt_comma = "TT_COMMA"
tt_list = "TT_LIST"
tt_range = "TT_RANGE"

keywords = [
    "manile",
    "che",
    "ma",
    "ne",
    "sarkhu",
    "alag",
    "motu",
    "nanu",
    "karta",
    "ane",
    "kyato",
    "nathi",
    "jo",
    "hoi",
    "naito",
    "paitu",
    "jya",
    "sudhi",
    "badha",
    "mate",
    "jelese",
    "mokalse",
    "kaini",
]


class Token:
    def __init__(self, pos_start, pos_end, type_, value=None):
        self.value = value
        self.tt = type_
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        if self.value:
            return f"{self.tt}: {self.value}"
        return f"{self.tt}"

    def copy(self):
        return Token(self.pos_start, self.pos_end, self.tt, self.value)


# lexer


class Lexer:
    def __init__(self, expr):
        self.expr = expr
        self.pos = Position()
        self.current_char = expr[0]
        with open("variables.json", "r") as f:
            self.variables = json.loads(f.read())

    def make_tokens(self):
        tokens = []
        while self.current_char and self.pos.idx < len(self.expr):
            pos_start = self.pos.copy()
            pos_end = self.pos.copy()
            pos_end.advance()
            if self.current_char == "+":
                tokens.append(Token(pos_start, pos_end, tt_add))
            elif self.current_char == "-":
                tokens.append(Token(pos_start, pos_end, tt_sub))
            elif self.current_char == "*":
                tokens.append(Token(pos_start, pos_end, tt_mul))
            elif self.current_char == "/":
                self.pos.advance()
                if self.expr[self.pos.idx] == "*":
                    self.pos.advance()
                    count = 1
                    while self.pos.idx < len(self.expr) and count != 0:
                        if self.expr[self.pos.idx] == "*":
                            if (
                                self.pos.idx < len(self.expr) - 1
                                and self.expr[self.pos.idx + 1] == "/"
                            ):
                                count -= 1

                        if self.expr[self.pos.idx] == "/":
                            if (
                                self.pos.idx < len(self.expr) - 1
                                and self.expr[self.pos.idx + 1] == "*"
                            ):
                                count += 1

                        self.pos.advance()
                else:
                    tokens.append(Token(pos_start, pos_end, tt_div))
            elif self.current_char == "(":
                tokens.append(Token(pos_start, pos_end, tt_lparam))
            elif self.current_char == ")":
                tokens.append(Token(pos_start, pos_end, tt_rparam))
            elif self.current_char == "[":
                tokens.append(Token(pos_start, pos_end, tt_list_start))
            elif self.current_char == "]":
                tokens.append(Token(pos_start, pos_end, tt_list_end))
            elif self.current_char == "#":
                tokens.append(Token(pos_start, pos_end, tt_comment))
            elif self.current_char == "\n":
                tokens.append(Token(pos_start, pos_end, tt_new_line))
            elif self.current_char == ",":
                tokens.append(Token(pos_start, pos_end, tt_comma))
            elif self.current_char == ".":
                if (
                    self.pos.idx < len(self.expr) - 3
                    and self.expr[self.pos.idx + 1] == "."
                    and self.expr[self.pos.idx + 2] == "."
                ):
                    val = tokens.pop()
                    if val.tt != tt_range:
                        val = val.value
                    self.pos.advance(self.expr[self.pos.idx])
                    self.pos.advance(self.expr[self.pos.idx])
                    self.pos.advance(self.expr[self.pos.idx])
                    num, error = self.make_number(True)
                    if error:
                        return None, error
                    tokens.append(Token(pos_start, pos_end, tt_range, (val, num.value)))

            elif self.current_char == "/":
                self.pos.advance()
                if self.expr[self.pos.idx] == "*":
                    self.pos.advance()
                    while self.pos.idx < len(self.expr):
                        if self.expr[self.pos.idx] == "*":
                            if (
                                self.pos.idx < len(self.expr) - 1
                                and self.expr[self.pos.idx + 1] == "/"
                            ):
                                break
                        self.pos.advance()
            elif self.current_char in [" ", "\t"]:
                tab_count = 0
                count = 0
                while self.pos.idx < len(self.expr) and self.expr[self.pos.idx] in [
                    " ",
                    "\t",
                ]:
                    if self.expr[self.pos.idx] == " ":
                        count += 1
                    else:
                        tab_count += 1
                    self.pos.advance(self.expr[self.pos.idx])
                tab_value = (
                    self.variables["tab"]
                    if self.variables["mode"] == 1
                    else self.variables["terminal tab"]
                )
                tab_count = tab_count * tab_value
                if tokens[-1].tt == tt_new_line:
                    tokens.append(
                        Token(pos_start, self.pos.copy(), tt_indent, count + tab_count)
                    )
                self.pos.idx -= 1

            elif self.current_char == '"':
                initial_pos = self.pos.copy()
                match = self.current_char
                value = ""
                self.pos.advance(self.expr[self.pos.idx])
                while (
                    self.pos.idx < len(self.expr) and self.expr[self.pos.idx] != match
                ):
                    value = value + self.expr[self.pos.idx]
                    self.pos.advance(self.expr[self.pos.idx])
                if self.pos.idx >= len(self.expr):
                    return None, Error(
                        "StringNotClosed",
                        f"{initial_pos} aaiya je string chalu thai ee bandh nathi kari",
                    )
                end_idx = self.pos.copy()
                end_idx.advance()
                tokens.append(Token(initial_pos, end_idx, tt_string, value))
            elif self.current_char == "'":
                initial_pos = self.pos.copy()
                match = self.current_char
                value = ""
                self.pos.advance(self.expr[self.pos.idx])
                while (
                    self.pos.idx < len(self.expr) and self.expr[self.pos.idx] != match
                ):
                    value = value + self.expr[self.pos.idx]
                    self.pos.advance(self.expr[self.pos.idx])
                if self.pos.idx >= len(self.expr):
                    return None, Error(
                        "StringNotClosed",
                        f"{initial_pos} aaiya je string chalu thai ee bandh nathi kari",
                    )
                end_idx = self.pos.copy()
                end_idx.advance()
                tokens.append(Token(initial_pos, end_idx, tt_fstring, value))
            elif self.current_char in digits + ".":
                token, error = self.make_number()
                if error:
                    return None, error
                tokens.append(token)
                continue
            elif self.current_char.lower() in chars:
                word = self.make_word()
                pos_end = self.pos.copy()
                pos_end.advance()
                if word in keywords:
                    tokens.append(Token(pos_start, pos_end, tt_keyword, word))
                elif word == "kharu":
                    tokens.append(Token(pos_start, pos_end, tt_true, "kharu"))
                elif word == "khotu":
                    tokens.append(Token(pos_start, pos_end, tt_false, "khotu"))
                else:
                    tokens.append(Token(pos_start, pos_end, tt_identifier, word))
                continue
            elif repr(self.current_char) in [repr("\t")]:
                pass
            elif self.current_char == " ":
                pass
            else:
                return None, InvalidCharacter(
                    f"{repr(self.current_char)} {self.pos} aa character samaj nai padi"
                )
            self.pos.advance(self.expr[self.pos.idx])
            if self.pos.idx >= len(self.expr):
                break
            self.current_char = self.expr[self.pos.idx]
        return tokens, None

    def make_word(self):
        word = ""
        while self.current_char.lower() in chars:
            word = word + self.current_char
            self.pos.advance(self.expr[self.pos.idx])
            if self.pos.idx >= len(self.expr):
                break
            self.current_char = self.expr[self.pos.idx]
        return word

    def make_number(self, force_int=False):
        dots = 0
        number = ""
        start = self.pos.copy()
        while True:
            if self.current_char in digits:
                number = number + self.current_char
            elif self.current_char in ".":
                if dots == 0:
                    dots += 1
                    number = number + self.current_char
                else:
                    return None, InvalidNumber(f"{self.pos} aa number khoto che")
            else:
                break
            self.pos.advance(self.expr[self.pos.idx])
            if self.pos.idx >= len(self.expr):
                break
            self.current_char = self.expr[self.pos.idx]
        end = self.pos.copy()
        end.advance()
        if force_int:
            number = number.replace(".", "")
            return Token(start, end, tt_int, int(number)), None
        if dots == 1:
            return Token(start, end, tt_double, float(number)), None
        return Token(start, end, tt_int, int(number)), None
