# k5

An experimental language to play with some ideas I've had. My 1st goal is to simply get this to work as an interpreted language. 


Another goal is to have as much checking being able to happen at compile-type as possible. If I can't add a meter to a second, there is no reason I should have to run the program to find that out. To this end, it should be strongly statically typed.

Basic multiprocessing primitives are also a goal for later, but I'm trying to design the language around that goal.

## Records

Records are a basic tool in k5.  The can be declared in two ways. The first uses indention, like python

    Person as {:
        fname as String
        lname as String
        age as Integer

and the second is a more traditional comma-separated list

    Person as { fname as String, lname as String, age as Integer }

To create a record, to call a method, lets say there are analogous ways

    {:
        fname => "Me"
        lname => "Surname"
        age => 0

and

    { fname => "Me", lname => "Surname", age => 0 }

Functions
---------

To define a function a signature and body are given (It can optionally be assigned to a variable)

    Born <= `{fname as String, lname as String} -> new_person as Person`:
        new_person <= Person {fname => fname, lname => lname, age => 0}

    Inc <= `{n as Integer} -> n1 as Integer`:
        n1 <= n + 1

The type of a composite function can be calculated

    add_two := Inc { n => Inc }

Notice that the parameters are named.

Not the preferred style
Done only to illustrate the {} vs {: syntax

    Age <= `{:
        person as Person
     -> older_person as Person`:
        older_person <= Person {:
            person + {:
                age => Inc {n => person.age}

## Casts

We can define casts from type to type as well. (Note, to use Print you need to have a record -> string method defined

    Cast Person as String <= `{_self as Person} -> s as String`:
        s <= _self.fname << " " << _self.lname << " (Age: " << _self.age << ")"

## Simple assignments

    Print {msg: Type of Born } # => {fname as String, lname as String} -> Person

Note the currying!

    keener_born <= Born { lname => "Keener" }

    Print {msg: Type of keener_born } # => {fname as String} -> Person

    p <= keener_born { fname => "Jim" }

A variable can never be modified.

    p <= keener_born { fname => "Jan" } # Error, p is defined
    p.age <= 0 # Error, p.age is already defined

## Functional

### Fold

Folds apply a function to a running accumulator and 
a value from the list. Folds cannot be parallelized.
Note the long form of a lambda.

    four_yr_old <= Fold {:
        list => [0..3]
        init => p
        over => `{_acc as Person, _item as Integer} -> _racc as Integer`:
            _racc <= Age { person => _acc }
            p <= _racc # This is OK because functions create their own, isolated, scope
            If {:
                test => _racc.age = 2
                then => Print { msg: "Oh noez! He's Terrible!" }
                else => Print { msg: _racc }

This would print:

    Jim Keener (Age: 1)
    Oh noez! He's Terrible!
    Jim Keener (Age: 3)
    Jim Keener (Age: 4)


`Fold` is an alias for `Foldl` (left-associative fold). `Foldr` is the complimentary right-associative fold. 

### Map

Maps apply a function to each element of an array, returning an array
Maps may be parallelized. Note the short form of the lambda; this can be used for simple expressions.

    two_to_seven <= Map {:
        list => [1..5]
        over => add_two {n: _item}

If we make the param for add_two \_item1, then we could do:
 
    two_to_seven <= Map {:
        list => [1..5]
        over => add_two

And since it's all statically typed we can verify that this'll work out.

Alternatively we could have done

    two_to_seven <= add_two { n: [1..5] } # (Except we'd have to give it a different name;)

and the map is done implicitly

### Reduce

Reduce works by applying the function over each slice of 2 of 
params in the by function of the array or a value from a previous
invocation until there are no more values left. All values are only
processed a single time

For example, the following calls reduce the list to the min of the list
Reduces may be parallelized.

Long form lambda:

    one <= Reduce {:
        list => [1..5]
        by => `{_item1 as Integer, _item2 as Integer} -> _ret as Integer`:
            _ret <= If {:
                test => _item1 < _item2
                then => _item1
                else => _item2

Short form lambda (since it's a single expression)

    one <= Reduce {:
        list => [1..5]
        by => If {:
                test => _item1 < _item2
                then => _item1
                else => _item2

Or use the built-in min function

    one <= Reduce {:
        list => [1..5]
        by => Min

    one <= Reduce { list => [1..5], by => Min }

One possible path of reduction could be

    1         2        3         4         5
     \       /          \       /         /
      \     /            \     /         /
       \   /              \   /         /
        min(1,2)->1        min(3,4)->3 /
         \                  \         /
          \                  \       /
           \                  \     /
            \                  \   /
             \                  min(3,5) -> 3
              \                 /
               \               /
                \             /
                 \           /
                  \         /
                   \       /
                    \     /
                     \   /
                      min(1,3)->1

Note that we could do sums this way too (instead of a fold). This gains us the ability to parallelize it as well

    fifteen <= Reduce { list => [1..5], by => Sum }

One possible path of reduction could be

    1         2        3         4         5
     \       /          \       /         /
      \     /            \     /         /
       \   /              \   /         /
        sum(1,2)->3        sum(3,4)->7 /
         \                  \         /
          \                  \       /
           \                  \     /
            \                  \   /
             \                  sum(7,5) -> 12
              \                 /
               \               /
                \             /
                 \           /
                  \         /
                   \       /
                    \     /
                     \   /
                      sum(3,12)->15

Since we can curry, we can do things like

    factorial <= Reduce { list => [1..n], by => Prod }

    Print { msg: Type of factorial } # => {n as Integer} -> Integer

    Print {msg: factorial {n: 5} } #=> 120

Pretty much any commutative and associative operation could be done via a `Reduce` operation. `Reduce` is a tree-like fold.

### Filter

We can also filter lists
The following returns \[2,4\].
Filters may be parallelized

    evens <= Filter {:
        list => [1..5]
        by => item % 2 = 0

Contrived example of nesting
returns \[4,8\].

    double_evens <= Map {:
        list => Filter {:
            list => [1..5]
            by => item % 2 = 0
        over: item * 2

## Units

Units are like units in real life.  They make sure that the numeric values we are talking about are measuring/representing the same thing. I feel that units make this easier than having classes for everything and easier to read.

Seconds are pre-defined

SI prefixes become defined for all units:

| yotta|10^24|
| zetta|10^21|
| eksa |10^18|
| peta |10^15|
| tera |10^12|
| giga |10^9 |
| mega |10^6 |
| kilo |10^3 |
| hecto|10^2 |
| deca |10^1|
| decy |10^-1|
| centy|10^-2|
| milli|10^-3|
| mikro|10^-6|
| nano |10^-9|
| pico |10^-12|
| femto|10^-15|
| atto |10^-18|
| zepto|10^-21|
| yokto|10^-24|

If one unit has a conversion, it can be done in both directions

Units can be "chained" if they can be converted to each other and the final type

Units can be composed via * and / to form complex units

If conversions are given as a Numeric, then a conversion in both directions is possible. If the conversions are given as an expression, then only that conversion is possible. (Note: Should I invert math expressions?)

Example

    meter as Unit {:
        foot => 3.28084
    foot as Unit {:
        inch => 12
    inch as Unit

    length := 1_foot_3_inch

    Print {msg: length } #=> 0.3809999 meter
    length2 := 1.453_kilometer
    Print {msg: length } #=> 1453 meter
    length3 := 1_453_meter
    Print {msg: length } #=> 1453 meter

    length4 := 1meter
    Print {msg: length4 } #=> 1 meter
    Print {msg: 2 * length4 }  #=> 2 meter
    Print {msg: length4 * length4 }  #=> 1 meter^2

    speed := 1 meter/sec
    Print {msg: speed } #=> 1 meter / sec
    Print {msg: speed * 4_sec } #=> 4 meter
    Print {msg: speed / 4_meter } #=> 0.25 sec^-1

    length5 := 1 + 1_meter # Compile time error
    length6 := 1_sec # Compile time error

## Tables as Functions

~ means that it can be any valid member of the set

All elements in a set must be represented in the table

### Example (Won't compile)

    states as Set [:begin, :middle, :end]
    transition <= `{s as ~states} -> return as ~states`:
        | s      | return  |
        +--------+---------+
        | :begin | :middle |
        | :middle| :end    |

All elements of the set need to be defined


### Example (Will compile)

    states as Set [:begin, :middle, :end]
    transition <= `{s as ~states} -> return as ~states`:
        | s      | return  |
        +--------+---------+
        | :begin | :middle |
        | :middle| :end    |
        | :end   | :end    |

    final? <= `{s as ~states} => return as Bool`:
        | s      | return  |
        +--------+---------+
        | :begin | False   |
        | :middle| False   |
        | :end   | True    |

    transition(:begin) #=> :middle
    final?(:middle) #=> False
    final?(:end) #=> True


## Language built-ins

### Base Types

* None
* Symbol
* Bool
* Numeric
 * Integer
 * Decimal
* String
* List
* Set
* Record

### Units

* Length
 * meter
 * foot
 * inch
 * yard
 * mile
* Time
 * second
 * minute
 * hour
 * day
* Volume
 * liter
 * tbs
 * tsp
 * oz
 * cup
 * pint
 * quart
 * pottle
 * gallon
* Temperature
 * fahrenheit
 * celsius
 * kelvin
 

### Functions

#### Utility

Note: Working on how to do this based on a "Comparable" type. Perhaps it could be done based
on operator definitions?

    Min <= `{_item1 as Numeric, _item2 as Numeric} -> Numeric`
    Max <= `{_item1 as Numeric, _item2 as Numeric} -> Numeric`
    Sum <= `{_item1 as Numeric, _item2 as Numeric} -> Numeric`
    Prod <= `{_item1 as Numeric, _item2 as Numeric} -> Numeric`
    Print <= `{msg as String}->None`

#### Functional

The @ before an identifier represents that the identifier is an unknown type.  Essentially it's similar to templates in Java.

    Foldl <= `{list => @x[], init => @y, over => `{_item as @x, _accum as @y} -> @y` } -> @y`
    Foldr <= `{list => @x[], init => @y, over => `{_item as @x, _accum as @y} -> @y` } -> @y`
    Map <= `{list => @x[], over => `{_item as @x } -> @y` } -> @y[]`
    Reduce <= `{list => @x[], by => `{_item1 as @x, _item2 as @x } -> @x` } -> @x `
    Filter <= `{list => @x[], by => `{_item as @x } -> Bool`} -> @x[]`

Some derived functions

    Fold <= `{list => @x[], init => @y, over => `{_item as @x, _accum as @y} -> @y` } -> @y`
    Reject <= `{list => @x[], by => `{_item as @x } -> Bool`} -> @x[]`

