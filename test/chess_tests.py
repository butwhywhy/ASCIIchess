from chess_rules import *
from sys import exit

pos = Position(position=[('king', True, 'a8'), ('pawn', True, 'g5'), ('king', False, 'a1'), ('pawn', False, 'h4')])
for m in pos.moves('pawn', False, 3, 7):
    print m

#exit(0)

pos = Position()
print moves_generator('pawn', True, False, 1)
print moves_generator('pawn', False, False, 1)

for m in pos.moves('pawn', False, 1, 0):
    print m

print
for m in pos.all_moves():
    print m

print
pos = pos.move('d4')
for m in pos.all_moves():
    print m

print

pos = pos.move('c5')
for m in pos.all_moves():
    print m

print
pos = pos.move('dxc5')
for m in pos.all_moves():
    print m

print
pos = pos.move('Nf6')
for m in pos.all_moves():
    print m

print

pos = pos.move('e4')
pos = pos.move('e6')
pos = pos.move('e5')
pos = pos.move('b5')
#pos = pos.move('a4')
#pos = pos.move('Bb7')
for m in pos.all_moves():
    print m

print
pos = pos.move('cxb6')
pos = pos.move('Bc5')
pos = pos.move('exf6')

for m in pos.all_moves():
    print m

print
pos = pos.move('Nc6')
pos = pos.move('fxg7')
pos = pos.move('Qf6')
for m in pos.all_moves():
    print m

print
pos = pos.move('gxh8=Q')
for m in pos.all_moves():
    print m

print

print pos.is_check()
pos = pos.move('Ke7')
pos = pos.move('Nc3')
pos = pos.move('Qxf2++')
for m in pos.all_moves():
    print m

print
print pos.is_check()
print pos.white_moves
print pos.is_mate()
