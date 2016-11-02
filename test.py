from parse import *

a = parse("Point({p}) = {x},{y},{z},{s}","Point(0) = -9.23706e-16,2.84217e-16,4.44089e-17,7.4685")
print(a)
print(a['x'])
