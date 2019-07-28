from vsc.types import to_expr
from vsc.impl.ctor import push_constraint_scope, push_constraint_stmt, pop_expr,\
    pop_constraint_scope, in_constraint_scope, last_constraint_stmt
from vsc.model.constraint_if_else_model import ConstraintIfElseModel
from vsc.model.constraint_scope_model import ConstraintScopeModel
from vsc.model.constraint_implies_model import ConstraintImpliesModel
from vsc.model.constraint_unique_model import ConstraintUniqueModel

#   Copyright 2019 Matthew Ballance
#   All Rights Reserved Worldwide
#
#   Licensed under the Apache License, Version 2.0 (the
#   "License"); you may not use this file except in
#   compliance with the License.  You may obtain a copy of
#   the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in
#   writing, software distributed under the License is
#   distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
#   CONDITIONS OF ANY KIND, either express or implied.  See
#   the License for the specific language governing
#   permissions and limitations under the License.

'''
Created on Jul 23, 2019

@author: ballance
'''

class constraint_t():
    
    def __init__(self, c):
        self.c = c
        pass
    
    def elab(self):
        print("elab")
    
def constraint(c):
    return constraint_t(c)

class if_then():

    def __init__(self, e):
        if not in_constraint_scope():
            raise Exception("Attempting to use if_then constraint outside constraint scope")
        
        to_expr(e)
        self.stmt = ConstraintIfElseModel(pop_expr())
        push_constraint_stmt(self.stmt)
        
    def __enter__(self):
        self.stmt.true_c = ConstraintScopeModel()
        push_constraint_scope(self.stmt.true_c)
        
    def __exit__(self, t, v, tb):
        pop_constraint_scope()
        
        
class else_if():

    def __init__(self, e):
        
        if not in_constraint_scope():
            raise Exception("Attempting to use if_then constraint outside constraint scope")
        
        last_stmt = last_constraint_stmt()
        if last_stmt == None or not isinstance(last_stmt, ConstraintIfElseModel):
            raise Exception("Attempting to use else_if where it doesn't follow if_then")
        
        to_expr(e)
        # Need to find where to think this in
        while last_stmt.false_c != None:
            last_stmt = last_stmt.false_c
            
        self.stmt = ConstraintIfElseModel(pop_expr())
        last_stmt.false_c = self.stmt
        
    def __enter__(self):
        self.stmt.true_c = ConstraintScopeModel()
        push_constraint_scope(self.stmt.true_c)
        
    def __exit__(self, t, v, tb):
        pop_constraint_scope()
        
class else_then():

    def __init__(self):
        if not in_constraint_scope():
            raise Exception("Attempting to use if_then constraint outside constraint scope")
        
        last_stmt = last_constraint_stmt()
        if last_stmt == None or not isinstance(last_stmt, ConstraintIfElseModel):
            raise Exception("Attempting to use else_then where it doesn't follow if_then/else_if")
        
        # Need to find where to think this in
        while last_stmt.false_c != None:
            last_stmt = last_stmt.false_c
            
        self.stmt = ConstraintScopeModel()
        last_stmt.false_c = self.stmt
        
    def __enter__(self):
        push_constraint_scope(self.stmt)
        
    def __exit__(self, t, v, tb):
        pop_constraint_scope()        

class implies():

    def __init__(self, e):
        if not in_constraint_scope():
            raise Exception("Attempting to use if_then constraint outside constraint scope")
        
        to_expr(e)
        self.stmt = ConstraintImpliesModel(pop_expr())
        
    def __enter__(self):
        push_constraint_stmt(self.stmt)
        push_constraint_scope(self.stmt)
        
    def __exit__(self, t, v, tb):
        pop_constraint_scope()        

def unique(*args):
    expr_l = []
    for i in range(-1, -(len(args)+1), -1):
        to_expr(args[i])
        expr_l.insert(0, pop_expr())
        
    push_constraint_stmt(ConstraintUniqueModel(expr_l))