from lexer import Token
from parser import (
    BinaryNode,
    ConditionNode,
    FunctionCall,
    FunctionNode,
    UnaryNode,
    VariableNode,
    WhileNode,
    ListNode,
    ForNode,
)
from lexer import *


class Interpreter:
    def __init__(self, ast):
        self.ast = ast

    def interpret(self, identifiers, local_identifiers=None):
        identifiers.pop("res", 1)
        for node in self.ast.nodes:
            if type(node) == VariableNode:
                if type(node.value) in [UnaryNode, BinaryNode]:
                    identifiers[node.name] = self.solve_expr(node.value, identifiers)
                elif type(node.value) in [Token, ListNode]:
                    if node.value.tt == tt_fstring:
                        print(1)
                        value = node.value.value
                        i = 0
                        dic = {}
                        while i < len(value):
                            identifier = ""
                            start = i
                            if value[i] == "{":
                                i += 1
                                while i < len(value) and value[i] != "}":
                                    identifier = identifier + value[i]
                                    i += 1
                                dic[start] = [identifier, i + 1]
                            i += 1
                        keys = list(dic.keys())
                        keys.reverse()
                        for i in keys:
                            value = value.replace(
                                value[i : dic[i][1]],
                                str(identifiers.setdefault(dic[i][0], "")),
                            )
                        identifiers[node.name] = value
                    elif node.value.tt == tt_list:
                        lst = self.get_list(identifiers, node.value)
                        identifiers[node.name] = lst
                    else:
                        identifiers[node.name] = self.solve_expr(
                            node.value, identifiers
                        )
            elif type(node) in [BinaryNode, UnaryNode]:
                identifiers["res"] = self.solve_expr(node, identifiers)
            elif type(node) == ConditionNode:
                for i in range(len(node.condition)):
                    if self.solve_expr(node.condition[i], identifiers):
                        interpret = Interpreter(node.program[i])
                        interpret.interpret(identifiers)
                        break
            elif type(node) == WhileNode:
                while self.solve_expr(node.condition, identifiers):
                    interpret = Interpreter(node.program)
                    interpret.interpret(identifiers)
            elif type(node) == ForNode:
                if node.iterable.value in identifiers.keys():
                    for i in identifiers[node.iterable.value]:
                        identifiers[node.iteration_var.value] = i
                        interpret = Interpreter(node.program)
                        interpret.interpret(identifiers)
                else:
                    for i in identifiers["global"][node.iterable.value]:
                        identifiers[node.iteration_var.value] = i
                        interpret = Interpreter(node.program)
                        interpret.interpret(identifiers)
            elif type(node) == FunctionNode:
                identifiers[node.name] = node
            elif type(node) == FunctionCall:
                name = node.name
                print(identifiers.keys())
                if name in list(identifiers.keys()):
                    func = identifiers[name]
                    interpreter = Interpreter(func.code)
                    temp = identifiers
                    temp.update(identifiers["global"])
                    dic = {"global": temp}

                    interpreter.interpret(temp)
                else:
                    func = identifiers["global"][name]

    def get_list(self, identifiers, node):
        lst = []
        for elem in node.elements:
            if type(elem) == ListNode:
                lst.append(self.get_list(identifiers, elem))
                continue
            res = self.solve_expr(elem, identifiers)
            lst.append(res)
        return lst

    def get_range(self, tpl):
        if type(tpl[0]) == Token:
            return list(
                range(
                    tpl[0].value[0],
                    tpl[0].value[1],
                    tpl[1],
                )
            )
        return list(range(tpl[0], tpl[1]))

    def solve_expr(self, expr, identifiers):
        if type(expr) == BinaryNode:
            tt = expr.token.tt
            value = expr.token.value
            if type(expr.left) == Token:
                if expr.left.tt != tt_identifier:
                    left = expr.left.value
                elif expr.left.value in identifiers.keys():
                    left = identifiers[expr.left.value]
                elif expr.left.value in identifiers["global"].keys():
                    left = identifiers["global"][expr.left.value]
            else:
                left = self.solve_expr(expr.left, identifiers)

            if value in ["ane", "kyato"]:
                if value == "ane" and left == False:
                    return False
                if value == "kyato" and left == True:
                    return True
            if type(expr.right) == Token:
                if expr.right.tt != tt_identifier:
                    right = expr.right.value
                elif expr.right.value in identifiers.keys():
                    right = identifiers[expr.right.value]
                elif expr.right.value in identifiers["global"].keys():
                    right = identifiers["global"][expr.right.value]
            else:
                right = self.solve_expr(expr.right, identifiers)
            if tt == tt_add:
                return left + right
            elif tt == tt_sub:
                return left - right
            elif tt == tt_mul:
                return left * right
            elif tt == tt_div:
                return left / right
            elif tt == tt_keyword:
                if value == "sarkhu":
                    return left == right
                elif value == "alag":
                    return left != right
                elif value == "motu":
                    return left < right
                elif value == "nanu":
                    return left > right
                elif value == "nanusarkhu":
                    return left >= right
                elif value == "motusarkhu":
                    return left <= right
                elif value == "ane":
                    return left and right
                elif value == "kyato":
                    return left or right
        if type(expr) == Token:
            if type(expr.value) == tuple:
                return self.get_range(expr.value)
            if expr.tt == tt_identifier:
                if expr.value in identifiers.keys():
                    if identifiers[expr.value] == "kharu":
                        return True
                    elif identifiers[expr.value] == "kharu":
                        return False
                    return identifiers[expr.value]
                else:
                    if identifiers["global"][expr.value] == "kharu":
                        return True
                    elif identifiers["global"][expr.value] == "kharu":
                        return False
                    return identifiers["global"][expr.value]
            if expr.value in ["kharu", "khotu"]:
                return True if expr.value == "kharu" else False
            return expr.value

        if type(expr) == UnaryNode:
            tt = expr.token.tt
            value = expr.token.value
            if type(expr.right) == Token:
                if tt in [tt_add, tt_sub]:
                    return (
                        expr.right.value
                        if expr.token.tt == tt_add
                        else -expr.right.value
                    )
                if tt == tt_keyword and value == "nathi":
                    if expr.right.tt == tt_identifier:
                        if expr.right.value in identifiers.keys():
                            return (
                                False
                                if identifiers[expr.right.value] == "kharu"
                                else True
                            )
                        else:
                            return (
                                False
                                if identifiers["global"][expr.right.value] == "kharu"
                                else True
                            )
                    return False if expr.right.tt == tt_true else True

            else:
                value = self.solve_expr(expr.right, identifiers)
                if tt in [tt_add, tt_sub]:
                    return value if expr.token.tt == tt_add else -value
                if tt == tt_keyword and expr.token.value == "nathi":
                    return False if value else True
