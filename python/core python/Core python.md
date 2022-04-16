# 1 Big pic



## The big pic

why py

what makes py unique

should i learn more

## Agenda

simple to learn

simple to use

great community

widely used

high demand

### simple to learn

easy to read and understand

### simple to use

focus on simplicity

focus on beasuty

### Great community

python.org/community

python.org/dev/peps

### High demand

### widely used

many diff uses

> web dev
>
> > api
> >
> > > flask 
> > >
> > > bottle
> > >
> > > pyramid
> >
> > websie
> >
> > > django
> > >
> > > turbogears
> > >
> > > web2py
> >
> > app(cms, erp)
> >
> > > plone
> > >
> > > django-cms
> > >
> > > mezzanine
>
> data sci
>
> > big data
> >
> > ml
> >
> > > spam
> > >
> > > network intrusion detection
> > >
> > > optical characer recognition
> > >
> > > computer vision
>
> edu and learning
>
> > stem
> >
> > programming
> >
> > hardware
> >
> > jupyter
>
> scripting
>
> > marchine scripting
> >
> > app scripting

## what is python

> syntax
>
> general-purpose
>
> multi-paradigm
>
> interpreted
>
> garbage-collected
>
> dynamically-typed

### Uniq syntax

use indent, not like c, using ; and {}

### General-purpose

> web dev
>
> data sci
>
> stem
>
> edu
>
> scripting

### Multi-paradigm

programming paradigms

> structured programming
>
> > control structures
> >
> > >  if then
> > >
> > > while
> >
> > subroutines
> >
> > > procedures
> > >
> > > func
> > >
> > > methods
>
> object-oriented programming
>
> > build on structure programming and how to communicate with each obj 
>
> func programming
>
> > build on structure programing

### Interpreted

CPU only actept its own lang, ISA: instruction set architechture

compiling : translate program into instruction

interpreted: live translation

### garbage-collection

von neumann architecture

cpu <--read-- Mem

cpu --write--> mem

Why care abt garbage collection?

> no tedious mem bookkeeping
>
> avoid comm mem leaks
>
> prevent whole classes of security issues
>
> efficiently imp certian persistent data structure

### dynamically typed

static typing

>  num = 1
>
> num = '123' report err

dynamic typing

> type is changing over lifetime of var
>
> type checking happens at runtime

Duck type: if it walks like a duck and it quacks like a duck, it must be a duck!

### Py pros and cons

pros

> comprehensive std lib
>
> > std lib philosophies
> >
> > > minimal std lib: pay only for what u use
> > >
> > > Comprehensive std lib: u can do all
> > >
> > > >  collections:
> > > >
> > > > file I/O
> > > >
> > > > Dates and times
> > > >
> > > > compression
> > > >
> > > > user interfaces
>
> community-driven
>
> > python.org/dev/peps
>
> 3rd party lib
>
> > pypi
> >
> > alibaba
> >
> > tinghua
>
> 3rd party tools
>
> > IDE
> >
> > >  pydev
> > >
> > > pycharm
> > >
> > > vs code
> > >
> > > spyder
> >
> > Editor
> >
> > > sublime
> > >
> > > vim
> > >
> > > notepad++
> >
> > py code tools
> >
> > > flake8: style guide enforcement
> > >
> > > pylint: code analysis
> > >
> > > block: code formatter

> cons
>
> > slow
> >
> > not native: high mem usage, lack of native security sandbox
> >
> > dynamic: runtime err

# 2 Get Started

## course overview

py fundamental data types

using functions and modules

py's underlying obj modle

defining ur own types using classes

working with iteration

## installing and starting py

### installing py

> win
>
> mac
>
> linux

### interactive py

read -> evaluate -> print -> loop -> read

### significant whitespace

pep 8

pep 20: import this

### py culture

### the py std lib

## 2.3 scalar types, operators, and control flow

relational operators

== , !=, >, >=, <, <=

control flow

while-loops



## 2.4 introducing strings, collections, and iteration

**Overview**

str, bytes, list, and dict

for-loop

put it all together

**str**

**str literals**

> multiline string: all u enter str more than one line

> > """ this is multi str"""

**string features**

**unicode in strings**

**bytes**

b =  b'some byte'

**list**

**dict**

> {k1: v1, k2: v2}

**for-loop**

**all together**

> from urllib.request import urlopen
>
> story = urlopen('http://sixty-norty.com/c/t.txt')
>
> story_words = []
>
> for line in story:
>
> ​    line_words = line.split()
>
> ​    for work in line_words:
>
> ​        sotry_words.append(work)
>
> story.close()



## 2.5 modularity

**func**

> def square(x):
>
> ​    return x * x

naming special func: \_\_feature\_\_

\_\_name\_\_ : specially named variable allowing us to detect whether a module is run as a script or imported into another module.

**Python exec model:**

> py module: convenient import with API
>
> py script: convenient exec from the cmd line
>
> py program: perhaps composed of many modules

**CMD Line args**

see words.py

**docstring**

literal strings which doc func, modles, and classes

they must be the first statement in the blocks for these constructs.

>  pep 257: official py convention for docstrings, not widely adopted.
>
> Sphinx: tool to create HTML doc from python docstrings

**Comments**

**shebang**

#!/usr/bin/env python3



## 2.6 obj and types



in progress



## 2.7 build-in collections

## 2.8 exceptions

## 2.9 iteration and iterables

## 2.10 classes

## 2.11 file IO and resource managements





# 3 Organizing larger programs

## 3.1 Nesting modules with packages

Modules

> python's basic tool for organizing code
>
> Normally a single Python source file
>
> Load modules with import
>
> Represented by module objects

packages vs modules

> packages: generally directories
>
> modules:  geneerally files

Locate modules

it will check sys.path

> sys.path 
>
> > list of directories
> >
> > searched in order in import

ex.

create a directory that not in path, and create a module in that folder. then import will fail.

sys.path.append('to_include'), then import work.

pythonpath

> env variable
>
> sys.path
>
> win
>
> > set PYTHONPATH=path1; path2; path3
>
> linux
>
> > export PYTHONPATH=path1: path2:path3







## 3.2 Implementing packages

## 3.3 Namespace and executable packages

## 3.4 Recommended package layout





# 4 Function and Callables



Review prerequisites
python's concept of callables
classes are callable objects
lambdas: anonymous callable objects
determine if an object is callable

```python
Function types
Free functions: func defined at module scope
Methods: functions defined with a class definition
```

## Argument types

Positional arguments are matched with formal arguments by position, in order   
keyword arguments are matched with formal arguments by name  
The choice between the tow is made at the call site











## Functional-style programming in python

```python
map()
filter()
functool.redude()
combination of above
```

### map()

call a function for the ele in a seq, and producing a new seq with the return values.

```python
map(ord, 'the quick brown fox')
```



# 5 Classes and object-orientation



# 6 Build a static siet generator with python



# 7 Add extensions to a static site generator with python





# 8 implementing iterators iterables and collections



# 9 Build a personal budget report with python collections and iterables



# 10 Robust resource and error handling



# 11 Numeric types, dates, and times



# 12  Byte oriented programming



# 13 Decoding sensor data using python



# 14 Build your own CLI planner app using python abstract base classes



# 15 The numeric tower, conversion, and operators



# 16 Hashing and more collections



# 17 Advanced generators and coroutines



# 18 Unit testing with python 



# 19 Managing python packages and virtual environments



# 20 Python best practices for code quality

