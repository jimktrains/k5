# k5

An experimental language to play with some ideas I've had. The goal would be to compile to a mostly-native format.  I'm thinking something more bare-bones than the JVM that just provides some "little" things like memory and process management along with the standard library. Functionally, this could be along the lines of a library implementing things such as links to the OS process management and wrappers around malloc and free.

If I can get simple programs to compile to LLVM, I would be more than happy.

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

    Print {msg: Type of Born } # => {fname as String, lname as String} -> new_person as Person

Note the currying!

    keener_born <= Born { lname => "Keener" }

    Print {msg: Type of keener_born } # => {fname as String} -> new_person as Person

    p <= keener_born { fname => "Jim" }

A variable can never be modified.

    p <= keener_born { fname => "Jan" } # Error, p is defined
    p.age <= 0 # Error, p.age is already defined

## Functional

### Fold

Folds apply a function to a running accumulator and 
a value from the list. Folds cannot be parallelized 

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

### Map

Maps apply a function to each element of an array, returning an array
Maps may be parallelized

    two_to_seven <= Map {:
        list => [1..5]
        over => `{_item as Integer} -> _ret as Integer`:
            _ret <= add_two(_item)

Alternatively we could have done

    two_to_seven <= add_two { n: [1..5] } # (Except we'd have to give it a different name;)

and the map is done implicitly

### Reduce

Reduce works by applying the function over each slice of 2 of 
params in the by function of the array or a value from a previous
invocation until there are no more values left. All values are only
processed a single time

For example, the following calls reduce the list to the min of the list
Reduces may be parallelized

    one <= Reduce {:
        list => [1..5]
        by => `{_item1 as Integer, _item2 as Integer} -> _ret as Integer`:
            _ret <= If {:
                test => _item1 < _item2
                then => _item1
                else => _item2
    one <= Reduce {:
        list => [1..5]
        by => Min

    one <= Reduce { list => [1..5], by => Min }

One possible path of reduction could be

    1         2        3         4         5
     \       /          \       /         /
      \     /            \     /         /
       \   /              \   /         /
        min                min         /
         \                  \         /
          \                  \       /
           \                  \     /
            \                  \   /
             \                  min
              \                 /
               \               /
                \             /
                 \           /
                  \         /
                   \       /
                    \     /
                     \   /
                      min


### Filter

We can also filter lists
The following returns \[2,4\].
Filters may be parallelized

    evens <= Filter {:
        list => [1..5]
        by => `{_item1 as Integer} -> _ret as Bool`:
            _ret <= _item % 2 = 0

Contrived example of nesting
returns \[4,8\].

    double_evens <= Map {:
        list => Filter {:
            list => [1..5]
            by => `{_item1 as Integer} -> _ret as Bool`:
                _ret <= _item % 2 = 0
        over: `{_item as Integer} -> _ret as Integer`:
            _ret <= _item * 2
