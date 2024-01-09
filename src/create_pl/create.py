#!/usr/bin/env python3
import pickle
import os

manual_pruning_list = {
    'program': [
        [[], [], [''], 0]
    ],
    'sourceElements': [
        [[('program', ['sourceElements', ' '])], [], [
            'sourceElement', ' ', 'sourceElement', ' '], 0],
        [[('program', ['sourceElements', ' '])], [], [
            'sourceElement', ' ', 'sourceElement', ' ', 'sourceElement', ' '], 0]
    ],
    'sourceElement': [
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ',
                                                                    'sourceElement', ' ', 'sourceElement', ' '])], [], ['export', ' ', 'statement'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', [
            'sourceElement', ' ', 'sourceElement', ' '])], [], ['export', ' ', 'statement'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', [
            'sourceElement', ' '])], [], ['export', ' ', 'statement'], 0],
        # [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement',
        #                                                             ' ', 'sourceElement', ' ', 'sourceElement', ' '])], [], [' ', 'statement'], 0],
        # [[('program', ['sourceElements', ' ']), ('sourceElements', [
        #     'sourceElement', ' ', 'sourceElement', ' '])], [], [' ', 'statement'], 0],
        # [[('program', ['sourceElements', ' ']), ('sourceElements',
        #                                          ['sourceElement', ' '])], [], [' ', 'statement'], 0]
    ],
    'statement': [
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['classDeclaration', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ']), ('sourceElement', [' ', 'statement'])], [], ['classDeclaration', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['classDeclaration', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['functionDeclaration', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ']), ('sourceElement', [' ', 'statement'])], [], ['functionDeclaration', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['functionDeclaration', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['debuggerStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ']), ('sourceElement', [' ', 'statement'])], [], ['debuggerStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['debuggerStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['tryStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['tryStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ', 'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['tryStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['throwStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['throwStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ', 'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['throwStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['switchStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ']), ('sourceElement', [' ', 'statement'])], [], ['switchStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['switchStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['labelledStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ']), ('sourceElement', [' ', 'statement'])], [], ['labelledStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['labelledStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['withStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['withStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ', 'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['withStatement', '\n'], 0],
        # [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['returnStatement', '\n'], 0],
        # [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['returnStatement', '\n'], 0],
        # [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ', 'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['returnStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['breakStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['breakStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ', 'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['breakStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['continueStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ']), ('sourceElement', [' ', 'statement'])], [], ['continueStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['continueStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['iterationStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ']), ('sourceElement', [' ', 'statement'])], [], ['iterationStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['iterationStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['ifStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['ifStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ', 'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['ifStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['expressionStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ']), ('sourceElement', [' ', 'statement'])], [], ['expressionStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['expressionStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['emptyStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['emptyStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ', 'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['emptyStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ']),
          ('sourceElement', [' ', 'statement'])], [], ['variableStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ']), ('sourceElement', [' ', 'statement'])], [], ['variableStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['variableStatement', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', [
            'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['block', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ',
                                                                    'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['block', '\n'], 0],
        [[('program', ['sourceElements', ' ']), ('sourceElements', ['sourceElement', ' ', 'sourceElement',
                                                                    ' ', 'sourceElement', ' ']), ('sourceElement', [' ', 'statement'])], [], ['block', '\n'], 0],
    ],
}


if __name__ == "__main__":
    pruning_list = manual_pruning_list
    file_name = "../create_pl/motivation_pruning_list.pickle"
    with open(file_name, "wb") as f:
        pickle.dump(pruning_list, f)
    print_dl(pruning_list)
    print(file_name)
