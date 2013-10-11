Ideas
* Static Types
* Map/Reduce built-ins

Modules
* defined by `module` keyword before a class

Classes
* Can have multiple inheritance

`None` is both a type and the only value of that type
`Bool` is a type where `True` and `False` are the only values

Basic data types
* Byte
* String
 * UTF-8
 * Immutable
* Int
 * 64-bit Signed Integer
* Decimal
 * 128-bit IEEE 754 Floating point
* APDecimal
 * Arbitrary precision floating point
* Array{type item}
* AArray{type key, type item}
 * Associative array/Hash table
* Func{type return, AArray{string, type} args}
* Stream{type item}

Example

    module main
    class Counter:
        Attributes:
            AArray{String, Int}(default:0) cnts
        Methods:
            None inc(String name):
                self.cnts[name] += 1
            Int __getitem__(String name):
                return self.cnts[name]

    module main
    class DoubleCount inherits Count:
        Methods:
            None inc(String name):
                self.cnts[name] += 1
            None inc2(String name):
                self.cnts[name] += 2

    module main
    class TripleCount inherits Count, DoubleCount:
        Resolve:
            inc as DoubleCount.inc
        Methods:
           None inc3(String name):
                self.cnts[name] += 3 

    TripleCount tc
    String("Blah") t

    p = "Test"

    tc.inc(t)
    print(tc[t]) # 1
    tc.inc2(t) 
    print(tc[t]) # 3
    tc.inc3(t) 
    print(tc[t]) # 6

Map/Reduce

map {mapable} over {Func}

map {mapable} with:
    {conditional}:
        {method}

reduce {mapable} by {Func}
