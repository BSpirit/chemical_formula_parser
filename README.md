# Chemical Formula

NB : python 3.9 was used to develop this module.

## Overview
This module can be used to parse a chemical formula.
The grammar used to parse the input is the following:
```
formula :=  molecule EOF
molecule := group molecule?
group := ATOM FACTOR? | OPENING_BRACKET molecule CLOSING_BRACKET FACTOR?

ATOM: '[A-Z][a-z]?'
FACTOR: '\d+'
OPENING_BRACKET: '[\[({]'
CLOSING_BRACKET: '[})\]]'
```

## Usage
```
>>> import chemical_formula
>>> formula = "Mg2[CH4{NNi2(Li2O4)5}14]3"
>>> lexer = chemical_formula.Lexer(formula)
>>> parser = chemical_formula.Parser(lexer)
>>> parser.parse_formula()
{'Mg': 2, 'C': 3, 'H': 12, 'N': 42, 'Ni': 84, 'Li': 420, 'O': 840}
```

## Run tests
```
python -m unittest
```
