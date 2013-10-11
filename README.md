k5
--

An experimental language to play with some ideas I've had. The goal would be to compile to a mostly-native format.  I'm thinking something more bare-bones than the JVM that just provides some "little" things like memory and process management along with the standard library.

Ideas
* Static Types
* Map/Reduce built-ins

Modules
* defined by `module` keyword before a class

Classes
* Can have multiple inheritance

Currying
* Methods can be curried.  Any method where named arguments are not passed essentially returns a curried method with the remaining named arguments


Basic data types
----------------
- None
 - `None` is the only value
- Bool
 -  `True` and `False` are the only values
- Byte
- String - UTF-8, Immutable
- Numeric
 - Int - 64-bit Signed Integer
 - Decimal - 128-bit IEEE 754 Floating point
 - APDecimal - Arbitrary precision floating point
 - CInt 
 - CDecimal
 - CAPDecimal
- Array{type item}
- AArray{type key, type item} - Associative array/Hash table
- Func{type return, AArray{string, type} args}
 - !{} enclose lambda expressions.
- Stream{type item}
- Unit
 - similar to units in real-life
 - sec second
 - can only be applied to numeric types
- Symbols
 - ruby-like
 - start with :
- Sets

Example

    @module main
    class Counter:
        Attributes:
            AArray{String, Int}(default:0) cnts
        Methods:
            None inc(String name):
                self.cnts[name] += 1
            Int __getitem__(String name):
                return self.cnts[name]

    @module main
    @inherits Count
    class DoubleCount:
        Methods:
            None inc(String name):
                self.cnts[name] += 1
            None inc2(String name):
                self.cnts[name] += 2

    @module main
    @inherits Count
    @inherits DoubleCount
    class TripleCount:
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
----------
Map/Reduce built-ins differ from `for` loops because map/Reduce calls may be parallelize and may not modify any variable not declared in the Func.

    map {mapable} over {Func}

Maps each item in the mapable through the function returning [Func(mappable0)] () (Hmm, to satisfy my editors need to make []() a link


    map {mapable} with:
        {conditional}:
            {method}

Similar to `map`, but may executes different functions for each element depending on the conditional

    reduce {mapable} by {Func}

Reduces the mapable by sending each element through the function as well as the accumulator (which d

Example

    Array a

    a = [1,2,3,4]

    map a over !{$1 * 2} #=> [2,4,6,8]

    map a with { #=> [1,4,3,8]
        !{$1 % 2 == 0}: {$1 * 2}
        !{True}: !{$1}
    }
    reduce a by !{$1 + $2} accumulator 0 #=> 10
    reduce a by !{$1 > $2 ? $1 : $2} accumulator -1000 #=> 4
    sum = !{reduce $1 by !{$1 + $2} accumulator 0}
    sum(a) #=> 10

Exceptions
----------

All thrown Exceptions must be declared and handled

Exception class need not be defined ahead of time. They will automatically be generated and inherit from exception

Example (Won't compile)

    Funcs:
        None add(Int x, Int y):
            if x == 2:
                throw AddingError("I don't like adding 2s!")

    add(2,3)

Example (Won't compile)

    Funcs:
        @throws AddingError
        None add(Int x, Int y):
            if x == 2:
                throw AddingError("I don't like adding 2s!")

    add(2,3)


Example (Will compile)

    Funcs:
        @throws AddingError
        None add(Int x, Int y):
            if x == 2:
                throw AddingError("I don't like adding 2s!")

    try:
        add(2,3)
    catch AddingError e:
        print(e.message)

Processes
---------

Shared-data Threads are evil.  Share-nothing threads or processes are nice.

Example

    @module main1
    @inherits process.service
    class service_runner
        Attributes:
            ProcessData pd
            Int cntr
        Methods:
            None __init__(ProcessData processdata):
                self.pd = pd
            Int counter():
                self.cntr += 1
                return self.cntr

    @module main2
    @inherits process.runnable
    class main:
        Attributes:
            main1.runner serv
            ProcessData pd
        Methods:
            None __init__(ProcessData processdata, main1.service_runner service):
                self.pd = pd
                self.serv = service
            None start():
                while True:
                    try:
                        print("%s: %s" % (self.pd.pid, self.serv.counter()))
                    catch ProcessFail e:
                        print(e)
                    sleep(1sec)

    Processes:
        Proc my_service:
            main1.service_runner
        Proc my_proc1:
            main2.main(service: my_service)
        Proc my_proc2:
            main2.main(service: my_service)

So, the way this is set up, it may be possible to run processes on other machines this would, more than likely be highly runtime-dependent.  Assuming a system similar to MPI hostsfile and that the user has host- or user- keys already distributed, something like the following could be done.

Hostfile:

    compy1:2
    compy2:1
    compy3:4

Program (same service and runnable defs as above)

    Processes:
        @Remote
        @MinCores 2
        Proc my_service:
            main1.service_runner
        Proc my_proc1:
            main2.main(service: my_service)
        Proc my_proc2:
            main2.main(service: my_service)

This will place `my_service` on compy1 or compy2.  Since the service is just a class, it is free to spawn other services or use map/reduce methods that can be parallelize.

Casts
-----

Examples

    Casts:
        Int x to CInt:
            return x + 0i

    class Count:
        Attributes:
            Int x
        Methods:
            None inc():
                self.x += 1
        Casts:
            to Int:
                return self.x
            to String:
                return "Count: " + (self.x as String)
            from Int y:
                Count a
                a.x = y
                return a

Units
-----

Units are like units in real life.  They make sure that the numeric values we are talking about are measuring/representing the same thing. I feel that units make this easier than having classes for everything and easier to read.

Seconds are pre-defined

SI prefixes become defined for all units:

- yotta 10^24
- zetta 10^21
- eksa  10^18
- peta  10^15
- tera  10^12
- giga  10^9 
- mega  10^6 
- kilo  10^3 
- hecto 10^2 
- deca  10^1
- decy  10^-1
- centy 10^-2
- milli 10^-3
- mikro 10^-6
- nano  10^-9
- pico  10^-12
- femto 10^-15
- atto  10^-18
- zepto 10^-21
- yokto 10^-24

If one unit has a conversion, it can be done in both directions

Units can be "chained" if they can be converted to each other and the final type

Units can be composed via * and / to form complex units

Example

    Unit meter:
        Conversions:
            foot: 3.28084
    Unit foot:
        Conversions:
            inch: 12
    Unit inch:
       pass

    meter length

    length = 1 foot 3 inch

    print(length) #=> 0.3809999 meter
    length = 1.453 kilometer
    print(length) #=> 1453 meter
    length = 1_453 meter
    print(length) #=> 1453 meter

    length = 1 meter
    print(length) #=> 1 meter
    print(2 * length)  #=> 2 meter
    print(length * length)  #=> 1 meter^2
    meter/sec speed
    speed = 1 meter/sec
    print(speed) #=> 1 meter / sec
    print(speed * 4 sec) #=> 4 meter
    print(speed / 4 meter) #=> 0.25 sec^-1

    speed = speed * 4 # Compile time error
    length = 1 + 1 meter # Compile time error
    length = 1 sec # Compile time error

Tables as Functions
-------------------

~ means that it can be any valid member of the set

All elements in a set must be represented in the table

Example (Won't compile)

    typedef Set(:begin, :middle, :end) as states
    Funcs:
        ~states Transition(~states s):
            | s      | return  |
            +--------+---------+
            | :begin | :middle |
            | :middle| :end    |

All elements of the set need to be defined


Example (Will compile)

    typedef Set(:begin, :middle, :end) as states
    Funcs:
        ~states Transition(~states s):
            | s      | return  |
            +--------+---------+
            | :begin | :middle |
            | :middle| :end    |
            | :end   | :end    |

        Bool Final?(~states s):
            | s      | return  |
            +--------+---------+
            | :begin | False   |
            | :middle| False   |
            | :end   | True    |

        Transition(:begin) #=> :middle
        Final?(:middle) #=> False
        Final?(:end) #=> True
