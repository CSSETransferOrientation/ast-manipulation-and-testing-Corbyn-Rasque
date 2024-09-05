#!/usr/bin/python3
import os
from os.path import join as osjoin
import unittest
from enum import Enum

# Use these to distinguish node types, note that you might want to further
# distinguish between the addition and multiplication operators
NodeType = Enum('BinOpNodeType', ['number', 'operator','variable'])

class BinOpAst():
    '''
    Reads input as a list of tokens in prefix notation, converts into internal representation,
    then can convert to prefix, postfix, or infix string output.
    '''
    def __init__(self, prefix_list):
        '''
        Initialize a binary operator AST from a given list in prefix notation.
        Destroys the list that is passed in.
        '''
        if prefix_list:
            self.val = prefix_list.pop(0)
            if self.val.lstrip("-").isnumeric():
                self.val = int(self.val)
                self.type = NodeType.number
                self.left = False
                self.right = False
            elif self.val.isalpha():
                self.type = NodeType.variable
                self.left = False
                self.right = False
            else:
                self.type = NodeType.operator
                self.left = BinOpAst(prefix_list)
                self.right = BinOpAst(prefix_list)

    def __str__(self, indent=0):
        '''
        Converts the binary tree into a printable string, where indentation
        indicates parent/child relationships
        '''
        ilvl = ' ' *indent
        left = '\n  ' + ilvl + self.left.__str__(indent+1) if self.left else ''
        right = '\n  ' + ilvl + self.right.__str__(indent+1) if self.right else ''

        return f"{ilvl}{self.val}{left}{right}"

    def __repr__(self):
        '''Generate the repr from the string'''
        return str(self)

    def prefix_str(self):
        '''
        Convert the BinOpAst to a prefix notation string.
        Makes use of new Python 3.10 case!
        '''
        match self.type:
            case NodeType.number:
                return str(self.val)
            case NodeType.variable:
                return str(self.val)
            case NodeType.operator:
                return str(self.val) + ' ' + self.left.prefix_str() + ' ' + self.right.prefix_str()

    def infix_str(self):
        '''
        Convert the BinOpAst to a prefix notation string.
        Makes use of new Python 3.10 case!
        '''
        match self.type:
            case NodeType.number:
                return str(self.val)
            case NodeType.variable:
                return str(self.val)
            case NodeType.operator:
                return '(' + self.left.infix_str() + ' ' + str(self.val) + ' ' + self.right.infix_str() + ')'
            
    def postfix_str(self):
        '''
        Convert the BinOpAst to a prefix notation string.
        Makes use of new Python 3.10 case!
        '''
        match self.type:
            case NodeType.number:
                return str(self.val)
            case NodeType.variable:
                return str(self.val)
            case NodeType.operator:
                return self.left.postfix_str() + ' ' + self.right.postfix_str() + ' ' + str(self.val)

    # ;;> Nice abstraction here to simplify implementation
    def identity(self, operator: str, match: int):
        '''
        For identity operations (specified by operator passed in), this replaces the
        node with values from the non-matching branch. Example: '*' , 1 or '+' , 0 
        '''
        if self.type != NodeType.operator:
            return
        
        self.left.identity(operator, match)
        self.right.identity(operator, match)

        if self.val == operator:
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
    
    def add_id(self):
        self.identity('+', 0)

    def mult_id(self):
        self.identity('*', 1)

    def mult_by_zero(self):
        '''
        Recursively traverses the tree to remove multiplication
        by 0 with 0 for a single iteration.
        '''
        if self.type != NodeType.operator:
            return
        
        self.left.mult_by_zero()
        self.right.mult_by_zero()

        if self.val == '*' and ((self.left.val == 0) or (self.right.val == 0)):
            self.type = NodeType.number
            self.val = 0
            self.left = self.right = False
            return
  
    def evaluate(self):
        '''
        Evaluates an expression between two numbers.
        '''
        self.type = NodeType.number
        match self.val:
            case '+':
                self.val = self.left.val + self.right.val
            case '-':
                self.val = self.left.val - self.right.val
            case '*':
                self.val = self.left.val * self.right.val
            case '/':
                self.val = int(self.left.val // self.right.val)
            case '%':
                self.val = int(self.left.val % self.right.val)
        self.left = self.right = False

    def constant_fold(self):
        '''
        Recursively traverses the tree and folds constants
        for a single iteration.
        '''

        if self.type != NodeType.operator:
            return
        
        self.left.constant_fold()
        self.right.constant_fold()

        if self.left.type == NodeType.number and self.right.type == NodeType.number:
            self.evaluate()
        else:
            self.add_id()
            self.mult_id()
            self.mult_by_zero()

    def simplify_binops(self):
        '''
        Simplify binary trees with the following, iteratively:
        1) Additive identity
        2) Multiplicative identity
        3) Multiplication by 0
        4) Constant folding
        '''
        # ;;> I would probably have made these functions like self.add_id and self.multi_id that just encapsulate these lines
        self.add_id()               # Additive Identity
        self.mult_id()              # Multiplicative Identity
        self.mult_by_zero()         # Multiplication by Zero
        self.constant_fold()        # Constant Folding

class BinOpAstTester(unittest.TestCase):
    ins = 'testbench'

    def operation_tester(self, function, test_type):
        '''
        Function to be tested will be passed in, along with the name if the folder within testbench containing the tests.
        '''
        for test_file in os.listdir(osjoin(self.ins, test_type, 'inputs')):
            if test_file[0] != '.':
                with open(osjoin(self.ins, test_type, 'inputs', test_file)) as test:
                    data = test.readline().strip()
                with open(osjoin(self.ins, test_type, 'outputs', test_file)) as solution:
                    expected = solution.readline().strip()
                print(f'Testing {test_type, test_file}')
                with self.subTest(msg=f'Testing {test_type}', inp=data, expected=expected):
                    result = BinOpAst(list(data.split()))
                    function(result)
                    result = result.prefix_str()
                    self.assertEqual(result, expected)

    def test_arith_id(self):
        self.operation_tester(BinOpAst.add_id, 'Arithmetic_Identity')

    def test_mult_id(self):
        self.operation_tester(BinOpAst.mult_id, 'Multiplicative_Identity')

    def test_mult_zero(self):
        self.operation_tester(BinOpAst.mult_by_zero, 'Multiplication_By_Zero')

    def test_constant_fold(self):
        self.operation_tester(BinOpAst.constant_fold, 'Constant_Fold')

    def test_combined(self):
        self.operation_tester(BinOpAst.simplify_binops, 'Combined')

    # def test_all(self):
    #     print('\n')
    #     for test_type in os.listdir(self.ins):
    #         for test_file in os.listdir(osjoin(self.ins, test_type, 'inputs')):
    #             if test_file[0] != '.':
    #                 with open(osjoin(self.ins, test_type, 'inputs', test_file)) as test:
    #                     test_name = test.readline().strip()
    #                     data = test.readline().strip()
    #                 with open(osjoin(self.ins, test_type, 'outputs', test_file)) as solution:
    #                     expected = solution.readline().strip()
    #                 # print(f'Testing {test_name}')
    #                 with self.subTest(msg=f'Testing {test_name}', inp=data, expected=expected):
    #                     result = BinOpAst(list(data.split()))
    #                     result.simplify_binops() # ;;> All of your tests are testing all of the functions with this line
    #                     # ;;> Which works but could make tracking bugs down confusing depending on the shape of the test
    #                     # ;;> It's generally better to test one thing specifically so that your bug chasing starts with fewer options
    #                     result = result.prefix_str()
    #                     self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main(argv=[''], verbosity=2, exit=False)