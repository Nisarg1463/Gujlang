from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
import sys

# getopt for command line options

identifiers = {"global": {}}

if len(sys.argv) == 1:
    while True:
        command = input("Enter > ")
        if command == "bandh":
            break
        lexer = Lexer(command)
        tokens, error = lexer.make_tokens()
        del lexer
        if error:
            print(error)
            continue

        # print(tokens)

        parser = Parser(tokens)
        ast, error = parser.make_tree()
        del parser

        if error:
            print(error)
            continue

        print(ast, error)

        interpreter = Interpreter(ast)
        interpreter.interpret(identifiers)
        del interpreter

        print(identifiers)
    # 1+(3-6)/5+78-52/(34*2)
    # 77.635294117647058823
else:
    file_name = sys.argv[1]
    with open(file_name, "r") as file:
        lexer = Lexer(file.read())
        tokens, error = lexer.make_tokens()
        del lexer
        if error:
            print(error)
            exit(1)

        # print(tokens)

        parser = Parser(tokens)
        ast, error = parser.make_tree()
        del parser

        if error:
            print(error)
            exit(1)

        # print(ast.nodes[1].args)
        # print(ast)

        interpreter = Interpreter(ast)
        interpreter.interpret(identifiers)
        del interpreter

        print(identifiers)
