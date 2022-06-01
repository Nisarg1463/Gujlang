from errors import *
from copy import deepcopy
from lexer import *

# parser


class Index:
    def __init__(self, idx):
        self.idx = idx

    def value(self):
        return self.idx

    def copy(self):
        return Index(self.idx)

    def advance(self):
        self.idx += 1

    def decend(self):
        self.idx -= 1

    def __repr__(self):
        return f"{self.idx}"


class ListNode:
    tt = tt_list

    def __init__(self):
        self.elements = []

    def __repr__(self):
        return str(self.elements)


class FunctionCall:
    def __init__(self, args, name):
        self.args = args
        self.name = name


class FunctionNode:
    def __init__(self, code, args, name):
        self.code = code
        self.args = args
        self.name = name


class ForNode:
    def __init__(self, iterable, program, var):
        self.iterable = iterable
        self.program = program
        self.iteration_var = var

    def __repr__(self):
        return f"{self.iterable}:{self.iteration_var}:{self.program}"


class WhileNode:
    def __init__(self, condition, program):
        self.condition = condition
        self.program = program

    def __repr__(self):
        return f"{self.condition}:{self.program}"


class ConditionNode:
    def __init__(self):
        self.condition = []
        self.program = []

    def add(self, condition, program):
        self.condition.append(condition)
        self.program.append(program)

    def __repr__(self):
        return f"{self.condition}: {self.program}"


class ProgramNode:
    def __init__(self):
        self.nodes = []

    def __repr__(self):
        rep = ""
        for i in self.nodes:
            rep = rep + f" {i}"
        return rep


class VariableNode:
    def __init__(self, name, value):
        self.name = name.value
        self.value = value
        self.pos_start = name.pos_start

    def __repr__(self):
        return f"{self.name} : {self.value}"


class BracketNode:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tt = "PriorityBrackets"
        self.pos_start = tokens[0].pos_start

    def __repr__(self):
        temp = ""
        for token in self.tokens:
            temp = temp + f"{token} "
        return temp


class BinaryNode:
    def __init__(self, left, token, right):
        self.left = left
        self.token = token
        self.right = right
        self.pos_start = token.pos_start

    def __repr__(self):
        return f"[{self.left} {self.token} {self.right}]"


class UnaryNode:
    def __init__(self, token, right):
        self.token = token
        self.right = right
        self.pos_start = token.pos_start

    def __repr__(self):
        return f"[{self.token} {self.right}]"


class Parser:
    def __init__(self, tokens, indent=0):
        self.tokens = tokens
        self.idx = Index(-1)
        self.idx.advance()
        self.length = len(tokens)
        self.updated = []
        self.flag = False
        self.indent = indent

    def make_tree(self):
        ast = ProgramNode()
        iteration = Index(0)
        condition_node = None
        line_start = iteration.copy()
        while iteration.value() < len(self.tokens):
            flag = False
            if self.tokens[iteration.value()].tt == tt_keyword:
                if self.tokens[iteration.value()].tt == tt_new_line:
                    line_start = iteration.copy()
                if self.tokens[iteration.value()].value == "manile":
                    check_index = iteration.value() + 2
                    if check_index < len(self.tokens):
                        token = self.tokens[check_index]
                        if token.tt == tt_keyword and token.value == "ma":
                            temp = check_index + 1
                            while temp < len(self.tokens):
                                token2 = self.tokens[temp]
                                if token2.tt == tt_keyword and token2.value == "che":
                                    break
                                temp += 1
                            if temp >= len(self.tokens):
                                return None, Error(
                                    "SyntaxError",
                                    f"{token.pos_start} aana pachi 'che' lakhvanu baaki che value pate tya 'che' lakho",
                                )
                            start = Index(check_index + 1)
                            end = Index(temp)
                            expr, error = self.make_bin_expr(start, end)
                            iteration.idx = end.idx
                            if expr:
                                ast.nodes.append(
                                    VariableNode(self.tokens[check_index - 1], expr)
                                )
                            elif check_index + 1 == temp - 1:
                                ast.nodes.append(
                                    VariableNode(
                                        self.tokens[check_index - 1],
                                        self.tokens[check_index + 1],
                                    )
                                )
                        else:
                            if token.tt == tt_identifier:
                                return None, Error(
                                    "SyntaxError",
                                    f"AA su laikhu che {token.pos_start} variable name khotu che",
                                )
                            else:
                                return None, Error(
                                    "SyntaxError",
                                    f"AA su laikhu che {token.pos_start} aaiya 'ma' lakho",
                                )
                    else:
                        None, Error(
                            "SyntaxError",
                            f"AA su laikhu che {token.pos_start} aaiya aaju agad lakho ke value shu che",
                        )
                elif self.tokens[iteration.value()].value == "jo":
                    flag = True
                    if condition_node:
                        ast.nodes.append(condition_node)
                        condition_node = None
                    condition_node = ConditionNode()
                    iteration.advance()
                    save = iteration.copy()
                    while iteration.value() < len(self.tokens):
                        if (
                            self.tokens[iteration.value()].tt == tt_keyword
                            and self.tokens[iteration.value()].value == "hoi"
                        ):
                            break
                        iteration.advance()
                    else:
                        return None, Error(
                            "SyntaxError",
                            f'{self.tokens[save.value()].pos_start} aana pachi "hoi nathi"',
                        )
                    condition, error = self.make_bin_expr(save, iteration)
                    if error:
                        return None, error
                    iteration.advance()
                    iteration.advance()
                    save = iteration.copy()
                    while iteration.value() < len(self.tokens) - 1:
                        if self.tokens[iteration.value()].tt == tt_new_line and (
                            self.tokens[iteration.value() + 1].tt != tt_indent
                            or self.tokens[iteration.value() + 1].value <= self.indent
                        ):
                            break
                        iteration.advance()
                    iteration.advance()
                    if self.tokens[save.value()].tt != tt_indent:
                        return None, Error("UnexpectedError", "creator ne contact karo")
                    parser = Parser(
                        self.tokens[save.value() : iteration.value()],
                        self.tokens[save.value()].value,
                    )
                    ast2, error = parser.make_tree()
                    if error:
                        return None, error
                    condition_node.condition.append(condition)
                    condition_node.program.append(ast2)
                    iteration.decend()
                elif self.tokens[iteration.value()].value == "naito":
                    flag = True
                    if condition_node == None:
                        return None, Error(
                            "SyntaxError",
                            f'{self.tokens[iteration.value()].pos_start} aa na pehla "jo" lakhvu padse',
                        )
                    iteration.advance()
                    if (
                        self.tokens[iteration.value()].tt == tt_keyword
                        and self.tokens[iteration.value()].value == "jo"
                    ):
                        iteration.advance()
                        save = iteration.copy()
                        while iteration.value() < len(self.tokens):
                            if (
                                self.tokens[iteration.value()].tt == tt_keyword
                                and self.tokens[iteration.value()].value == "hoi"
                            ):
                                break
                            iteration.advance()
                        else:
                            return None, Error(
                                "SyntaxError",
                                f'{self.tokens[save.value()].pos_start} aana pachi "hoi nathi"',
                            )
                        condition, error = self.make_bin_expr(save, iteration)
                        if error:
                            return None, error
                        iteration.advance()
                        iteration.advance()
                        save = iteration.copy()
                        while iteration.value() < len(self.tokens) - 1:
                            if self.tokens[iteration.value()].tt == tt_new_line and (
                                self.tokens[iteration.value() + 1].tt != tt_indent
                                or self.tokens[iteration.value() + 1].value
                                <= self.indent
                            ):
                                break
                            iteration.advance()
                        iteration.advance()
                        if self.tokens[save.value()].tt != tt_indent:
                            return None, Error(
                                "UnexpectedError", "creator ne contact karo"
                            )
                        parser = Parser(
                            self.tokens[save.value() : iteration.value()],
                            self.tokens[save.value()].value,
                        )
                        ast2, error = parser.make_tree()
                        if error:
                            return None, error
                        condition_node.condition.append(condition)
                        condition_node.program.append(ast2)
                    else:
                        iteration.advance()
                        save = iteration.copy()
                        while iteration.value() < len(self.tokens) - 1:
                            if self.tokens[iteration.value()].tt == tt_new_line and (
                                self.tokens[iteration.value() + 1].tt != tt_indent
                                or self.tokens[iteration.value() + 1].value
                                <= self.indent
                            ):
                                break
                            iteration.advance()
                        iteration.advance()
                        if self.tokens[save.value()].tt != tt_indent:
                            return None, Error(
                                "UnexpectedError", "creator ne contact karo"
                            )
                        parser = Parser(
                            self.tokens[save.value() : iteration.value()],
                            self.tokens[save.value()].value,
                        )
                        ast2, error = parser.make_tree()
                        if error:
                            return None, error
                        condition_node.condition.append(
                            Token(None, None, tt_true, True)
                        )
                        condition_node.program.append(ast2)
                    iteration.decend()
                elif self.tokens[iteration.value()].value == "jya":
                    iteration.advance()
                    if (
                        self.tokens[iteration.value()].tt == tt_keyword
                        and self.tokens[iteration.value()].value == "sudhi"
                    ):
                        iteration.advance()
                        save = iteration.copy()
                        while iteration.value() < len(self.tokens):
                            if (
                                self.tokens[iteration.value()].tt == tt_keyword
                                and self.tokens[iteration.value()].value == "hoi"
                            ):
                                break
                            iteration.advance()
                        else:
                            return None, Error(
                                "SyntaxError",
                                f'{self.tokens[save.value()].pos_start} aana pachi "hoi nathi"',
                            )
                        condition, error = self.make_bin_expr(save, iteration)
                        if error:
                            return None, error
                        iteration.advance()
                        iteration.advance()
                        save = iteration.copy()
                        while iteration.value() < len(self.tokens) - 1:
                            if self.tokens[iteration.value()].tt == tt_new_line and (
                                self.tokens[iteration.value() + 1].tt != tt_indent
                                or self.tokens[iteration.value() + 1].value
                                <= self.indent
                            ):
                                break
                            iteration.advance()
                        iteration.advance()
                        if self.tokens[save.value()].tt != tt_indent:
                            return None, Error(
                                "UnexpectedError", "creator ne contact karo"
                            )
                        parser = Parser(
                            self.tokens[save.value() : iteration.value()],
                            self.tokens[save.value()].value,
                        )
                        ast2, error = parser.make_tree()
                        if error:
                            return None, error
                        ast.nodes.append(WhileNode(condition, ast2))

                    else:
                        return None, Error(
                            "SyntaxError",
                            f'{self.tokens[iteration.value()].pos_start} aaiya "sudhi" aave',
                        )
                elif self.tokens[iteration.value()].value == "ma":
                    iteration.advance()
                    if (
                        self.tokens[iteration.value()].tt == tt_keyword
                        and self.tokens[iteration.value()].value == "badha"
                    ):
                        iterable = self.tokens[iteration.value() - 2]
                        iteration.advance()
                        iteration_variable = self.tokens[iteration.value()]
                        iteration.idx += 3

                        save = iteration.copy()
                        while iteration.value() < len(self.tokens) - 1:
                            if self.tokens[iteration.value()].tt == tt_new_line and (
                                self.tokens[iteration.value() + 1].tt != tt_indent
                                or self.tokens[iteration.value() + 1].value
                                <= self.indent
                            ):
                                break
                            iteration.advance()
                        iteration.advance()
                        if self.tokens[save.value()].tt != tt_indent:
                            return None, Error(
                                "UnexpectedError", "creator ne contact karo"
                            )
                        parser = Parser(
                            self.tokens[save.value() : iteration.value()],
                            self.tokens[save.value()].value,
                        )
                        ast2, error = parser.make_tree()
                        if error:
                            return None, error
                        ast.nodes.append(ForNode(iterable, ast2, iteration_variable))

                    else:
                        return None, Error(
                            "SyntaxError",
                            f'{self.tokens[iteration.value()].pos_start} aaiya "badha" aave',
                        )
                elif self.tokens[iteration.value()].value == "jelese":
                    identifier = self.tokens[iteration.value() - 1]
                    start_idx = iteration.copy()
                    start_idx.advance()
                    while iteration.value() < len(self.tokens):
                        if self.tokens[iteration.value()].tt == tt_new_line:
                            break
                        iteration.advance()
                    args = deepcopy(self.tokens[start_idx.value() : iteration.value()])
                    iteration.advance()
                    save = iteration.copy()
                    while iteration.value() < len(self.tokens) - 1:
                        if self.tokens[iteration.value()].tt == tt_new_line and (
                            self.tokens[iteration.value() + 1].tt != tt_indent
                            or self.tokens[iteration.value() + 1].value <= self.indent
                        ):
                            break
                        iteration.advance()
                    iteration.advance()
                    if self.tokens[save.value()].tt != tt_indent:
                        return None, Error("UnexpectedError", "creator ne contact karo")
                    parser = Parser(
                        self.tokens[save.value() : iteration.value()],
                        self.tokens[save.value()].value,
                    )
                    ast2, error = parser.make_tree()
                    if error:
                        return None, error
                    ast.nodes.append(FunctionNode(ast2, args, identifier))
            elif self.tokens[iteration.value()].tt == tt_identifier:
                identifier_idx = iteration.copy()
                if (
                    iteration.value() < len(self.tokens) - 2
                    and self.tokens[iteration.value() + 1].tt == tt_lparam
                ):
                    save = iteration.copy()
                    save.advance()
                    while iteration.value() < len(self.tokens):
                        if self.tokens[iteration.value()].tt == tt_rparam:
                            args = []
                            if save.value() != iteration.value():
                                args = deepcopy(
                                    self.tokens[save.value() : iteration.value()]
                                )
                            break
                        iteration.advance()
                    ast.nodes.append(
                        FunctionCall(args, self.tokens[identifier_idx.value()].value)
                    )
            elif self.tokens[iteration.value()].tt == tt_comment:
                while (
                    iteration.value() < len(self.tokens)
                    and self.tokens[iteration.value()].tt != tt_new_line
                ):
                    iteration.advance()

            if not flag and condition_node:
                ast.nodes.append(condition_node)
                condition_node = None
            iteration.advance()
        if condition_node:
            ast.nodes.append(condition_node)
            condition_node = None
        if ast.nodes == []:
            ast2, error = self.make_bin_expr(Index(0), Index(len(self.tokens)))
            if error:
                return None, error
            ast.nodes.append(ast2)
        return ast, None

    def make_conditional_node(self, start, end):
        temp = start.copy()
        while temp.value() < end.value():
            if (
                self.tokens[temp.value()].tt == tt_keyword
                and self.tokens[temp.value()].value == "ne"
            ):
                oldtemp = temp.copy()
                left, error = self.make_bin_expr(start, temp)
                if error:
                    return None, error
                if temp.value() < oldtemp.value():
                    end.idx -= oldtemp.value() - temp.value()
                temp.advance()
                temp2 = temp.copy()
                while temp2.value() < end.value():
                    if self.tokens[temp2.value()].tt == tt_keyword and self.tokens[
                        temp2.value()
                    ].value in ["sarkhu", "alag"]:
                        break
                    temp2.advance()
                if temp2.value() >= end.value():
                    return None, Error(
                        "SyntaxError",
                        f'{self.tokens[temp.value()]} ane {self.tokens[temp2.value()]} ni vacche ["sarkhu","alag"] mathi ek lakhvanu rai gayu che',
                    )
                oldtemp = temp2.copy()
                right, error = self.make_bin_expr(temp, temp2)
                if error:
                    return None, error
                if temp2.value() < oldtemp.value():
                    end.idx -= oldtemp.value() - temp2.value()
                return BinaryNode(left, self.tokens[temp2.value()], right), None
            elif (
                self.tokens[temp.value()].tt == tt_keyword
                and self.tokens[temp.value()].value == "karta"
            ):
                oldtemp = temp.copy()
                left, error = self.make_bin_expr(start, temp)
                if error:
                    return None, error
                if temp.value() < oldtemp.value():
                    end.idx -= oldtemp.value() - temp.value()
                temp.advance()
                temp2 = temp.copy()
                while temp2.value() < end.value():
                    if self.tokens[temp2.value()].tt == tt_keyword and self.tokens[
                        temp2.value()
                    ].value in ["motu", "nanu"]:
                        break
                    temp2.advance()
                if temp2.value() >= end.value():
                    return None, Error(
                        "SyntaxError",
                        f'{self.tokens[temp.value()]} ane {self.tokens[temp2.value()]} ni vacche ["motu","nanu"] aa mathi ek lakhvanu rai gayu che',
                    )
                oldtemp = temp2.copy()
                right, error = self.make_bin_expr(temp, temp2)
                if error:
                    return None, error
                if temp2.value() < oldtemp.value():
                    end.idx -= oldtemp.value() - temp2.value()
                token = self.tokens[temp2.value()].copy()
                if temp2.value() + 2 < len(self.tokens):
                    if (
                        self.tokens[temp2.value() + 1].tt == tt_keyword
                        and self.tokens[temp2.value() + 1].value == "ne"
                    ):
                        if (
                            self.tokens[temp2.value() + 2].tt == tt_keyword
                            and self.tokens[temp2.value() + 2].value == "sarkhu"
                        ):
                            token.value = token.value + "sarkhu"
                return BinaryNode(left, token, right), None
            temp.advance()
        return None, None

    def make_conditional_expr(self, start, end):
        temp = start.copy()
        and_node = None
        if (
            self.tokens[end.value() - 1].tt == tt_keyword
            and self.tokens[end.value() - 1].value == "nathi"
        ):
            temp = end.copy()
            temp.decend()
            left, error = self.make_bin_expr(start, temp)
            if error:
                return None, error
            if end.value() - 1 > temp.value():
                end.idx -= end.value() - temp.value() - 1
            return UnaryNode(self.tokens[end.value() - 1], left), None

        while temp.value() < end.value():
            token = self.tokens[temp.value()]
            if token.tt == tt_keyword:
                if token.value == "kyato":
                    oldtemp = temp.copy()
                    left, error = self.make_bin_expr(start, temp)
                    if error:
                        return None, error
                    if oldtemp.value() > temp.value():
                        end.idx -= oldtemp.value() - temp.value()
                    right, error = self.make_bin_expr(Index(temp.value() + 1), end)
                    if error:
                        return None, error

                    return BinaryNode(left, token, right), None
                elif token.value == "ane":
                    oldtemp = temp.copy()
                    left, error = self.make_bin_expr(start, temp)
                    if error:
                        return None, error
                    if oldtemp.value() > temp.value():
                        end.idx -= oldtemp.value() - temp.value()
                    right, error = self.make_bin_expr(Index(temp.value() + 1), end)
                    if error:
                        return None, error

                    and_node = BinaryNode(left, token, right)
            temp.advance()
        if and_node:
            return and_node, None
        return None, None

    def make_list(self, start, end):
        temp = start.copy()
        while temp.value() < end.value():
            lst = ListNode()
            if self.tokens[temp.value()].tt == tt_list_start:
                save = temp.copy()
                temp.advance()
                elem_start = temp.copy()
                while temp.value() < end.value():
                    if self.tokens[temp.value()].tt == tt_list_start:
                        self.make_list(temp, end)
                    if self.tokens[temp.value()].tt == tt_list_end:
                        if elem_start.value() != temp.value():
                            save2 = temp.copy()
                            node, error = self.make_bin_expr(elem_start, temp)
                            if error:
                                return error
                            lst.elements.append(node)
                            if temp.value() < save2.value():
                                end.idx -= save2.value() - temp.value()
                        break
                    if self.tokens[temp.value()].tt == tt_comma:
                        save2 = temp.copy()
                        node, error = self.make_bin_expr(elem_start, temp)
                        if error:
                            return error
                        lst.elements.append(node)
                        if temp.value() < save2.value():
                            end.idx -= save2.value() - temp.value()
                        elem_start = temp.copy()
                        elem_start.advance()
                    temp.advance()
                else:
                    return Error(
                        "SyntaxError",
                        f"{self.tokens[save.Value()].pos_start} aa list band karo",
                    )
                oldlen = len(self.tokens)
                for _ in range(save.value(), temp.value() + 1):
                    self.tokens.pop(save.value())
                self.tokens.insert(save.value(), lst)
                end.idx -= oldlen - len(self.tokens)
            temp.advance()
            return None

    def make_bin_expr(self, start, end):

        error = self.make_list(start, end)
        if error:
            return None, error

        node, error = self.make_conditional_expr(start, end)
        if error:
            return None, error
        if node:
            return node, None

        node, error = self.make_conditional_node(start, end)
        if error:
            return None, error
        if node:
            return node, None

        if self.tokens[start.value()].tt in [tt_add, tt_sub]:
            node, error = self.make_bin_expr(Index(start.value() + 1), end)
            if error:
                return None, error
            return UnaryNode(self.tokens[0], node), None

        node, error = self.make_bin_node(start, end, [tt_add, tt_sub])
        if error:
            return None, error
        if node:
            return node, None

        node, error = self.make_bin_node(start, end, [tt_mul, tt_div])
        if error:
            return None, error
        if node:
            return node, None

        if end.value() - start.value() == 1:
            token = self.tokens[start.value()]
            if token.tt in [
                tt_double,
                tt_int,
                tt_identifier,
                tt_true,
                tt_false,
                tt_string,
                tt_fstring,
            ]:
                return token, None
            if type(token) == BracketNode:
                parser = Parser(token.tokens)
                ast, error = parser.make_tree()
                if error:
                    return None, error
                return ast.nodes[0], None
            if type(token) == ListNode:
                return token, None
        return None, Error(
            "NodeNotUnderstood",
            f"aa node samaj nai paido index {start.value()} thi {end.value()}",
        )

    def make_bin_node(self, start, end, token_types):
        oldlen = len(self.tokens)
        temp = end.copy()
        temp.decend()
        while temp.value() > start.value():
            if self.tokens[temp.value()].tt in token_types:
                oldtemp = temp.copy()
                left, error = self.make_bin_expr(start, temp)
                if error:
                    return None, error
                if oldtemp.value() != temp.value():
                    end.idx -= oldtemp.value() - temp.value()
                    oldtemp.idx = temp.value()
                temp.advance()
                right, error = self.make_bin_expr(temp, end)
                if error:
                    return None, error
                temp.decend()
                return BinaryNode(left, self.tokens[temp.value()], right), None
            elif self.tokens[temp.value()].tt == tt_rparam:
                temp2 = temp.copy()
                count = 1
                temp.decend()
                while count != 0 and temp.value() >= start.value():
                    if self.tokens[temp.value()].tt == tt_lparam:
                        count -= 1
                    elif self.tokens[temp.value()].tt == tt_rparam:
                        count += 1
                    temp.decend()
                if (
                    temp.value() < start.value()
                    and self.tokens[temp.value() + 1].tt != tt_lparam
                ):
                    return None, Error(
                        "BracketsNotBalanced",
                        f"bracket sarkha lakho {self.tokens[temp2.value()].pos_start} aaiya",
                    )
                tokens_lst = deepcopy(self.tokens[temp.value() + 2 : temp2.value()])
                for _ in range(temp.value(), temp2.value()):
                    self.tokens.pop(temp.value() + 1)
                self.tokens.insert(temp.value() + 1, BracketNode(tokens_lst))
                end.idx -= oldlen - len(self.tokens)
                temp.advance()
            temp.decend()
        return None, None
