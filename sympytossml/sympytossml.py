from sympy import *

def parse_ops_file(file_name):
    ops_f = open(file_name)
    ops = {}     
    
    for ln in ops_f:
        ln_lst = ln.split()
        op_name = ln_lst[0]
        ops[op_name] = list()
        for i in range(1, len(ln_lst)):
            ops[op_name].append(ln_lst[i])
    
    return ops

def op_structure(ops, op):
    if str(op) in ops:
        return ops[str(op)]
    else:
        r = [str(op), 'of', '0']
        return r 

def convert(expr, ops):
    if len(expr.args) == 0:  
        return str(expr)
    else:
        structure = op_structure(ops, expr.__class__.__name__)
        r = ""
        for e in structure:
            if e.isdigit():
                r += convert(expr.args[int(e)], ops)
            else:
                r += e
            r += ' '  
    return r;

ops = parse_ops_file('operators')

f, g = Function('f'), Function('g')
x, y, n = symbols('x y n')
test_expr = x + f(g(tan(n))) 
print_tree(test_expr, assumptions = False)
test_ssml = convert(test_expr, ops)

print(test_ssml)
