#/usr/bin/env python3

from __future__ import annotations

from ast import literal_eval
from time import sleep, time

# delete below after moving to .errors.py
#================================================

class InterpreterError(Exception):
    pass

class SegmentationFaultError(InterpreterError):
    def __init__(self, address) -> None:
        super().__init__(
            f'SegmentationFaultError: Tried to access out-of-bounds memory at address={address}.'
        )
        self.address = address

class InvalidProgramError(InterpreterError):
    pass

#================================================

def _subleq_interpreter(
        program: list[int],
        mem: dict[int, int],
        /
) -> list[int]:
    
    mem[-1] = 0
    
    if type(program) != list:
        raise InvalidProgramError(
            f'Program should be a list: got {program} of type={type(program)} instead.'
        )
    
    # load program into memory
    for i, v in enumerate(program):
        if type(v) != int:
            raise InvalidProgramError(
                f'Program should be a list of int: contains the element {v} of type={type(v)}'
            )
        
        mem[i] = v
    
    out: list[int] = [] # Result of the program
    pc:  int       = 0  # program counter

    while pc + 1:
        try:
            a, b, c = mem[pc], mem[pc + 1], mem[pc + 2]
            if b == -1:
                out.append(mem[a])
            
            else:
                mem[b] -= mem[a]
            
            pc = c if mem[b] <= 0 else pc + 3
        
        except KeyError as e:
            raise SegmentationFaultError(e.args[0])
    
    return out