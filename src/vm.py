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

def _subleq_assm(
    vars: dict[str, int],
    src: str,
    *,
    custom_defs: dict[str, str] | None = None
) -> list[int]:
    instrs: list[tuple[str, str, str]] = []
    labels: dict[str, int] = dict()
    
    curr_addr: int = 0
    for line in src.splitlines():
        line = line.split(';', maxsplit = 1)[0].strip()
        if len(line) == 0:
            continue
        
        operands: list[str] = []
        for operand in line.split(', '):
            if len(operand) == 0:
                continue
            
            if custom_defs is not None and operand in custom_defs:
                operand = custom_defs[operand]
            
            operands += operand,
        
        if len(operands) == 1 and operands[0].endswith(':'):
            label_name: str = operands[0][:-1]
            
            labels[label_name] = curr_addr
        
        elif len(operands) == 2:
            operands += [curr_addr + 3]
            instrs += tuple(operands),
            curr_addr += 3
        
        else:
            raise ValueError(f"Invalid operand: `{operands!r}`")
    
    var_addrs: dict[str, int] = dict()
    var_segmt: list[int] = []
    for var_name, init_val in vars.items():
        var_segmt += init_val,
        var_addrs[var_name] = curr_addr
        curr_addr += 1
    
    out: list[int] = []
    for line, instr in enumerate(instrs):
        (src_, dest, jmp) = instr
        if src_ == r'%zero':
            out += -1,
        
        elif src_ in vars:
            out += var_addrs[src_],
        
        else:
            try:
                out += int(src_),
            
            except ValueError:
                raise ValueError(f'{line=}: invalid src op: `{src_}`')
        
        if dest == r'%out':
            out += -1,
        
        elif dest in vars:
            out += var_addrs[dest],
        
        else:
            try:
                out += int(dest)
            
            except ValueError:
                raise ValueError(f'{line=}: invalid dest op: `{dest}`')
        
        if jmp == r'%halt':
            out += -1,
        
        elif jmp in labels:
            out += labels[jmp],
        
        else:
            try:
                out += int(jmp),
            
            except ValueError:
                raise ValueError(f'{line=}: invalid jmp op: `{jmp}`')
    
    out.extend(var_sgmt)
    return out
