# The Natscript Language

Natscript is a cross-platform, high-level, type-inferred, dynamic interpreted scripting language with a natural, prosaic syntax, built on top of Python (with easy cross-integration).

## First steps

### REPL Hello World

Let's start by writing our first program in the Natscript REPL shell. After [installing the natscript interpreter](https://github.com/rbaltrusch/natscript/tree/main/README.md#getting-started), open your terminal and run the `natscript` Python package, which will open our REPL shell:

```
python -m natscript

Natscript interpreter interactive shell (version: 0.1.0)
Type 'exit' to exit the shell.
>>>
```

Type `print "hello world"` in the REPL shell to run your first Natscript command, printing to standard output.

### Types and Variables

To assign a value to a variable, use the `set` command:

```python
set myVar to 1
```

To check the value of our variable, we can again print to standard output: ``print myVar`.

As we can see, we do not need to explicitly declare the type of our variable `myVar`. However, it does have a type, which is inferred by the Natscript interpreter (in this case, an integer).

There are a few built-in types:
- integer
- float
- string
- boolean (`true` or `false`)
-`nothing` (a `null` or `None` value)
- function: code that can be called on demand
- collection: a list of values
- structure: a collection of values with named

Note: we can also redeclare previously declared variables, with a different value or type, e.g.:

```python
set myVar to 1
set myVar to 2
set myVar to "something else"
```

Note also that there are no operators in the language, only statements (whose tokens cannot be redeclared, so they act as keywords). In fact, the only special punctuation/syntax in the language are optional commas, strings (`"hello"`), floats (`1.0`) and clauses (`if checked true then { }`).

#### Special variables

`it` and `itself` contain the value of the last referenced variable:

```python
set a to 1
print it  # prints value of a (i.e. 1)
```

This can be used for some well-flowing code, such as squaring a number: 

```python
set a to 4 then multiply it by itself  # 16
```

`result` is a special variable containing the return value of a called function.

```powershell
define function f as { return 2 }
call f and print result  # prints 2
```

It can also alternatively be used using the form `result of call`, e.g.:

```powershell
define function f as { return 2 }
print result of call f  # prints 2
```

Note: the `result` variable:
- is only available after a function call,
- contains only the return value of the last function call, and
- is discarded after being accessed once.

### Optional tokens

A number of optional tokens in Natscript can be specified for prosaic purposes, with no runtime effect, for example `and`, `,`, `then`, `that`, `is`, `are`.

This can, for example, be used to combine two statements on a single line:
```python
set a to 1
print it

# alternative one-liner
set a to 1 and print it
```
### Number operations

All operations in Natscript are done using statements, not operators:

```python
set a to 2, subtract 1 from it
multiply it by 3 and then print it  # prints 3
```

Note: numerical statements generally manipulate a variable in place, not a value, so `add 1 to 1` would result in a syntax error.

All operations:
- `add value to variable`
- `subtract value from variable`
- `multiply variable by value`
- `divide variable by value`
- `round variable`
- More number operations are found in the "math.nat" standard library.

### Conditionals

TODO

```powershell
set condition to true
# set condition to 3 greater than 1
if checked condition then {
    # runs if condition is true
} else {
    # runs if condition is false
}
```

Logical operators: `all`, `any`, `none`, `some`
Logical functions: `greater than`, `less than`, `identical to`, `equal to`, `contains`

### Collections

TODO

Define a sequence of numbers: `set mycollection to range from 1 to 5` (including start, excluding end, resulting in `[1, 2, 3, 4]`).

Access elements:
- `first`
- `last`
- `get variable from collection at index`
- Select a subset of elements: `set a to slice of collection from 1 to 3` (Note: this is a copy and does not modify the original collection)

Modify:
- `update collection at index to value`

Manipulation:
`reverse collection`
- Map elements: `apply myfunction to collection`
- Filter elements: `exclude numbers greater than 1 from collection` (Note: the provided variable name is a stylistic choice and has no functional impact)
- Sort in place: `sort collection`

### Loops

TODO

- `while condition { ... }`
- `for each element in collection { ... }`
- For-each loop with filter: `for each element in collection greater than 2 { ... }`

Control flow:
- To break out of a loop, use the `break out` statement.
- To continue to the next loop iteration, use the `skip` keyword. An optional variable name can be provided for stylistic reasons (with no runtime effect), e.g.: `skip it`.

### Functions

A simple function can be defined as follows:

```powershell
# define function
define function myFunction as {
    print "hello world"
}

# call function
call myFunction  # prints hello world
```

Functions can also take arguments and return values:

```powershell
# definition of a function returning sum of two numbers
define function add expecting [a, b] as {
    add a to b and return it
}

# print result of function call
print result of call add with [1, 2]  # prints 3
```

Note: functions can be nested, and return other functions. However, the usefulness of this is currently limited due to the missing support of closures (inner functions do not remember outer scopes).

For documentation of the `result` variable, check the documentation on [special variables](#special-variables).

It is also possible to specify default values:

```powershell
define function power expecting [a, b defaulting to 1] as {
    multiply it by a then return it
}

# call function not specifying b
call power with [2]  # returns 2

# alternative call with named function argument:
call power with [a defaulting to 2]
```

### Structures

Define structure and instantiate it:

```powershell
# definition
define structure MyStruct as {
    field1,
    field2
}

# instantiation
set myinstance to new MyStruct with ["something", 1]
print myinstance  # prints {'field1': something, 'field2': 1}
```

No inheritance is allowed, only composition. TODO

## Comments

Line comments can be included by prefixing them with `#`:

```powershell
#this is a comment
```

Long comments are currently not supported.

## Files, modules and Imports

To reuse Natscript code, save it to a file ending in `.nat` and run it with the Natscript interpreter:

```
python -m natscript myfile.nat
```

Previously defined Natscript files can be imported inside a Natscript file using their name or relative path (if defined in another folder). However, a list of tokens to be imported from the file must explicitly be specified.

For example, if we define a function `f` in the module `M1.nat`:

```powershell
# inside M1.nat
define function f as {
    print "hello"
}
```

We could then import that function f in another file `other.nat`:

```powershell
# inside other.nat
import [f] from "M1.nat"

call f
```

### Standard Library

The Natscript interpreter comes with a small standard library that contains several pre-installed Natscript modules:
- math.nat: math operations.
- bitwise.nat: bitwise operations.
- collections.nat: set and dict implementations.
- string.nat: for string manipulation.
- regex.nat: for regex support.
- types.nat: for type conversion functions.
- json.nat: for json support.
- system.nat: provides an interface to the OS.
- time.nat: provides time utilities.

They can be imported directly by name in the REPL or any Natscript source file, e.g.:

```powershell
import [absolute] from "math.nat"
```

Bytecode compiler with .natc: TODO

### Natscript search path

The Natscript interpreter manipulates the Python search path (`sys.path`) to find its modules. By default, the current directory is searched, as well as the path to the ``natscript_lib` folder.

The optional environment variable `NATSCRIPT_PATH` can be used to supply additional directories to be searched (list of semicolon-separated absolute paths).

Alternatively, the `sys.path` variable can be modified directly, e.g. as exposed in the "system.nat" standard library:

```powershell
import [path] from "system.nat" and append "C:/my/search/path" to it
```

### Integration with Python packages

Installed Python packages are directly importable inside any Natscript source file:

```powershell
import [defaultdict] from "collections.py" 
```

Note: the Python module to be imported from needs to be suffixed with a `.py` file extension.

### Access modifiers

Variables can be made `constant` or `private`.

Functions and structures can be made `private`.

## File IO

The content of text files can be read with `content of filepath`, while `write` can be used to write to a file:

```powershell
write "hello world" to "myfile.txt"
set text to content of "myfile.txt"
print text  # outputs hello world
```

Appending to the end of a text file instead of overwriting it can be done as follows:

```powershell
write "some text" to end of "myfile.txt"
```

## CLI options

TODO

## Error handling

TODO

`try` `catch` `raise` `exit`

- RunTimeException
- ValueException
- TypeException
- FileNotFoundException
- ImportException
