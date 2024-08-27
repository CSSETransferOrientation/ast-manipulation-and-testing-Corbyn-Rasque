#!/usr/bin/python3
import os
from os.path import join as osjoin

import unittest

from enum import Enum

# Use these to distinguish node types, note that you might want to further
# distinguish between the addition and multiplication operators
NodeType = Enum('BinOpNodeType', ['number', 'operator','variable'])

class BinOpAst():
    """
        Reads input as a list of tokens in prefix notation, converts into internal representation,
    then can convert to prefix, postfix, or infix string output.
    """
    def __init__(self, prefix_list):
        """
        Initialize a binary operator AST from a given list in prefix notation.
        Destroys the list that is passed in.
        """
        if prefix_list:
            self.val = prefix_list.pop(0)
            if self.val.isnumeric():
                self.val = int(self.val)
                self.type = NodeType.number
                self.left = False
                self.right = False
            else:
                self.type = NodeType.operator
                self.left = BinOpAst(prefix_list)
                self.right = BinOpAst(prefix_list)

    def __str__(self, indent=0):
        """
        Convert the binary tree printable string where indentation level indicates
        parent/child relationships
        """
        
        ilvl = ' ' *indent
        left = '\n  ' + ilvl + self.left.__str__(indent+1) if self.left else ''
        right = '  ' + ilvl + self.right.__str__(indent+1) if self.right else ''

        return f"{ilvl}{self.val}{left}{right}"

    def __repr__(self):
        """Generate the repr from the string"""
        return str(self)

    def prefix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        Make use of new Python 3.10 case!
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return self.val + ' ' + self.left.prefix_str() + ' ' + self.right.prefix_str()

    def infix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        Make use of new Python 3.10 case!
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return '(' + self.left.infix_str() + ' ' + self.val + ' ' + self.right.infix_str() + ')'
    def postfix_str(self):
        """
        Convert the BinOpAst to a prefix notation string.
        Make use of new Python 3.10 case!
        """
        match self.type:
            case NodeType.number:
                return self.val
            case NodeType.operator:
                return self.left.postfix_str() + ' ' + self.right.postfix_str() + ' ' + self.val

    def identity(self, operator: str, match: int):
        '''
        For identity operations (specified by operator passed in), this function replaces
        the node with values from the non-matching branch. Example: '*' , 1 or '+' , 0 
        '''
        if self.type == NodeType.number:
            return
        elif self.type == NodeType.operator and self.val == operator:
            if self.left.val == match:
                self.type = self.right.type
                self.val = self.right.val
                self.left = self.right.left
                self.right = self.right.right
                return
            elif self.right.val == match:
                self.type = self.left.type
                self.val = self.left.val
                self.right = self.left.right
                self.left = self.left.left
                return

        self.left.identity(operator, match)
        self.right.identity(operator, match)    
    
    def mult_by_zero(self):
        """
        Reduce multiplication by zero
        x * 0 = 0
        """
        pass
        # if self.type == NodeType.number:
        #     return

        # if self.val == '*' and ((self.left.val == 0) or (self.right.val == 0)):
        #     print('here')
        #     self.type = NodeType.number
        #     self.val = 0
        #     self.left = self.right = False

        # self.left.mult_by_zero()
        # self.right.mult_by_zero()
            
    def constant_fold(self):
        """
        Fold constants,
        e.g. 1 + 2 = 3
        e.g. x + 2 = x + 2
        """
        # Optionally, IMPLEMENT ME! This is a bit more challenging. 
        # You also likely want to add an additional node type to your AST
        # to represent identifiers.
        pass            

    def simplify_binops(self):
        """
        Simplify binary trees with the following:
        1) Additive identity, e.g. x + 0 = x
        2) Multiplicative identity, e.g. x * 1 = x
        3) Extra #1: Multiplication by 0, e.g. x * 0 = 0
        4) Extra #2: Constant folding, e.g. statically we can reduce 1 + 1 to 2, but not x + 1 to anything
        """
        self.identity('+', 0)   # Additive Identity
        self.identity('*', 1)   # Multiplicative Identity
        self.mult_by_zero()
        self.constant_fold()


if __name__ == "__main__":
    # unittest.main()
    test = '+ 1 * 0 + 7 + 5 0'
    # test = '* + 1 2 + 3 4'
    test_tree = BinOpAst(list(test.split()))
    print(test_tree)
    test_tree.simplify_binops()
    print(test_tree)
