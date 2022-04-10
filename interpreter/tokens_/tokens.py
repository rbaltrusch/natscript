# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:34 2020

@author: Korean_Crimson
"""
import operator
from typing import Optional
from interpreter.token_ import ClauseToken
from interpreter.token_ import ExpectedToken
from interpreter.token_ import Token


class VALUE(Token):
    def _run(self, interpreter):
        value = self.TOKEN_FACTORY.create_value(self.value)
        interpreter.stack_append(value)


class INTEGER(VALUE):
    VALUE_FACTORY = int


class FLOAT(VALUE):
    VALUE_FACTORY = float


class STRING(VALUE):
    # for whatever reason python is passing self as first arg
    VALUE_FACTORY = lambda _, x: str(x.strip('"'))


class TRUE(VALUE):
    def __init__(self, *_, **__):
        super().__init__(value=1)


class FALSE(VALUE):
    def __init__(self, *_, **__):
        super().__init__(value=0)


class NOTHING(VALUE):
    VALUE_FACTORY = lambda *_: None


class VARNAME(VALUE):
    def _run(self, interpreter):
        if interpreter.check_variable(self.value):
            variable = interpreter.get_variable(self.value)
        else:
            variable = self.TOKEN_FACTORY.create_variable(self.value)

        interpreter.stack_append(variable)
        interpreter.set_variable("it", variable)


class ASSIGN_R(Token):
    pass


class ASSIGN_L(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 2),
        ExpectedToken((ASSIGN_R,), 1),
        ExpectedToken((VALUE,), 0),
    ]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = value.get_value()
        interpreter.set_variable(variable.name, variable)


class FROM(Token):
    pass


class TIMES(Token):
    pass


class BY(Token):
    pass


class AS(Token):
    pass


class PRINT(Token):

    EXPECTED_TOKENS = [ExpectedToken((Token,))]

    def _run(self, interpreter):
        value = interpreter.stack_pop()
        print(value.get_value())


class ADD(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((ASSIGN_R,), 1),
        ExpectedToken((VARNAME,), 2),
    ]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = variable.get_value() + value.get_value()


class SUBTRACT(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((FROM,), 1),
        ExpectedToken((VARNAME,), 2),
    ]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = variable.get_value() - value.get_value()


class MULTIPLY(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 2),
        ExpectedToken((TIMES,), 1),
        ExpectedToken((VALUE,), 0),
    ]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = variable.get_value() * value.get_value()


class DIVIDE(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 2),
        ExpectedToken((BY,), 1),
        ExpectedToken((VALUE,), 0),
    ]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = variable.get_value() / value.get_value()
        if variable.value == int(variable.value):
            variable.value = int(variable.value)


class IT(VARNAME):
    def _run(self, interpreter):
        variable = interpreter.get_variable("it")
        interpreter.stack_append(variable)


class LINEBREAK(Token):
    def pop_tokens(self, tokens):
        return tokens.pop(0)

    def update_token_factory(self, token_factory):
        token_factory.line_number += 1


class COMMA(Token):
    def pop_tokens(self, tokens):
        return tokens.pop(0)


class COMMENT(Token):
    def pop_tokens(self, tokens):
        popped_tokens = []
        while tokens:
            token = tokens.pop(0)
            popped_tokens.append(token)
            if isinstance(token, LINEBREAK):
                break
        return popped_tokens


class AND(Token):
    def pop_tokens(self, tokens):
        return tokens.pop(0)


class END(Token):
    pass


class CLAUSE(VALUE, ClauseToken):

    CLOSE_TOKEN = END

    def run(self, interpreter):
        def run_tokens(interpreter):
            for token in self.tokens:
                token.run(interpreter)
                if isinstance(token, RETURN):
                    break
            else:
                interpreter.stack_append(self.TOKEN_FACTORY.create_value(value=None))

        value = self.TOKEN_FACTORY.create_value(run_tokens)
        interpreter.stack_append(value)


class FUNCTION(Token):
    def _run(self, interpreter):
        function = interpreter.stack_pop()
        code = interpreter.stack_pop()
        input_parameters = interpreter.stack_pop().get_value()
        function.value = code.get_value()
        function.inputs = input_parameters
        interpreter.set_variable(function.name, function)


class COLLECTION_END(Token):
    pass


class COLLECTION(VALUE, ClauseToken):

    CLOSE_TOKEN = COLLECTION_END

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._constructed = False

    def _run(self, interpreter):
        if self._constructed:
            return

        # ignore last token, which closes the collection (COLLECTION_END)
        self.value = []
        for _ in self.tokens[:-1]:
            value = interpreter.stack_pop()
            self.value.append(value)
        self.value.reverse()

        super()._run(interpreter)
        self._constructed = True


class EXPECTING(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((COLLECTION,), 0)
    ]


class WITH(Token):
    EXPECTED_TOKENS = [ExpectedToken((COLLECTION,), 0)]


class DEFINE(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((FUNCTION,), 4),
        ExpectedToken((VARNAME,), 3),
        ExpectedToken((EXPECTING,), 0, optional=True),
        ExpectedToken((AS,), 2),
        ExpectedToken((CLAUSE,), 1),
    ]

    def run(self, interpreter):
        if not self.has_all_optionals:
            value = self.TOKEN_FACTORY.create_value(value=[])
            interpreter.stack_append(value)
        super().run(interpreter)


class RETURN(Token):
    EXPECTED_TOKENS = [ExpectedToken((VALUE,), 0)]

class CALL(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME, CLAUSE), 1),
        ExpectedToken((WITH,), 0, optional=True)
    ]

    def _run(self, interpreter):
        function = interpreter.stack_pop()
        inputs = interpreter.stack_pop().get_value() if self.has_all_optionals else []
        interpreter.add_stack()
        # take input parameters from stack
        for value, variable in zip(inputs, function.inputs):
            interpreter.set_variable(variable.name, value)
        function.get_value()(interpreter)
        return_value = interpreter.stack_pop()
        interpreter.remove_stack()
        interpreter.set_variable('result', return_value)


class THEN(Token):
    pass


class ELSE(Token):
    EXPECTED_TOKENS = [ExpectedToken((CLAUSE,))]


class CONDITION(VALUE, ClauseToken):

    OPERATOR = operator.eq
    CLOSE_TOKEN = VALUE

    def _run(self, interpreter):
        second_value = interpreter.stack_pop().get_value()
        first_value = interpreter.stack_pop().get_value()
        condition_result = self.OPERATOR(first_value, second_value)
        value = self.TOKEN_FACTORY.create_value(condition_result)
        interpreter.stack_append(value)


class NOT(CONDITION):
    EXPECTED_TOKENS = [ExpectedToken((CONDITION,))]

    def _run(self, interpreter):
        value = interpreter.stack_pop()
        value.negate_value()
        interpreter.stack_append(value)


class CHECK(VALUE):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((CONDITION,), 1),
    ]

    def _run(self, interpreter):
        pass


class IF(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((VALUE, CHECK), 2),
        ExpectedToken((THEN,), 0),
        ExpectedToken((CLAUSE,), 3),
        ExpectedToken((ELSE,), 1, optional=True),
    ]

    def run(self, interpreter):
        super().run(interpreter)

    def _run(self, interpreter):
        if_clause = interpreter.stack_pop()
        condition_value = interpreter.stack_pop()
        else_clause = interpreter.stack_pop() if self.has_all_optionals else None
        if condition_value.get_value() == 1:
            if_clause.get_value()(interpreter)
        elif else_clause is not None:
            else_clause.get_value()(interpreter)

    @property
    def else_executed(self) -> bool:
        return self.has_else and self.tokens[-1].executed

    @property
    def has_else(self) -> bool:
        return isinstance(self.tokens[-1], ELSE)


class IN(Token):
    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = value.get_value()
        interpreter.set_variable(variable.name, variable)


class EACH(Token):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = 0
        self.collection = None

    # run order is ignored by EACH.run method
    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 1),
        ExpectedToken((IN,), 2),
        ExpectedToken((COLLECTION, VARNAME), 0),
    ]

    def run(self, interpreter):
        if self.collection is None:
            self.tokens[-1].run(interpreter)
            self.collection = interpreter.stack_pop().get_value()

        if self.exhausted:
            return

        value = self.collection[self._index]
        interpreter.stack_append(value)
        self._index += 1

        # ignore collection (last token), as it was previously run
        for token in self.tokens[:-1]:
            token.run(interpreter)

        # append it again, this value can be consumed by optional for-each
        # condition, or needs to be thrown away by for-each loop if no condition
        interpreter.stack_append(value)

    def reset(self):
        self._index = 0
        self.collection = None

    @property
    def exhausted(self) -> bool:
        if self.collection is None:
            return False
        return self._index >= len(self.collection)

class FOR(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((EACH,), 0),
        ExpectedToken((CONDITION,), 1, optional=True),
        ExpectedToken((CLAUSE,), 2),
    ]

    def run(self, interpreter):
        while not self.extractor.exhausted:
            for token in self.tokens:
                token.run(interpreter)
            clause = interpreter.stack_pop()
            if self._check_condition(interpreter):
                clause.get_value()(interpreter)
        self.extractor.reset()

    def _check_condition(self, interpreter) -> bool:
        value = interpreter.stack_pop()
        if self.condition is None:
            return True
        return value.get_value()

    @property
    def extractor(self) -> EACH:
        return self.tokens[0]

    @property
    def condition(self) -> Optional[CONDITION]:
        if not isinstance(self.tokens[1], CONDITION):
            return None
        return self.tokens[1]


class WHILE(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((CLAUSE,), 1),
    ]

    def run(self, interpreter):
        while True:
            for token in self.tokens:
                token.run(interpreter)
            clause = interpreter.stack_pop()
            if not self._check_condition(interpreter):
                break
            clause.get_value()(interpreter)

    def _check_condition(self, interpreter) -> bool:
        return interpreter.stack_pop().get_value()


class THAN(Token):
    pass


class GREATER(CONDITION):
    OPERATOR = operator.gt
    EXPECTED_TOKENS = [
        ExpectedToken((THAN,), 0),
        ExpectedToken((VALUE,), 1),
    ]

class EQUAL(CONDITION):
    OPERATOR = operator.eq
    EXPECTED_TOKENS = [
        ExpectedToken((ASSIGN_R,), 0),
        ExpectedToken((VALUE,), 1),
    ]

class LESS(CONDITION):
    OPERATOR = operator.lt
    EXPECTED_TOKENS = [
        ExpectedToken((THAN,), 0),
        ExpectedToken((VALUE,), 1),
    ]


class THE(Token):
    def pop_tokens(self, tokens):
        return tokens.pop(0)


tokens = {
    "set": ASSIGN_L,
    "to": ASSIGN_R,
    "from": FROM,
    "by": BY,
    "times": TIMES,
    "print": PRINT,
    "add": ADD,
    "subtract": SUBTRACT,
    "multiply": MULTIPLY,
    "divide": DIVIDE,
    "it": IT,
    "and": AND,
    "true": TRUE,
    "false": FALSE,
    "\n": LINEBREAK,
    ",": COMMA,
    "[": COLLECTION,
    "]": COLLECTION_END,
    "define": DEFINE,
    "function": FUNCTION,
    "as": AS,
    "{": CLAUSE,
    "}": END,
    "return": RETURN,
    "nothing": NOTHING,
    "call": CALL,
    "if": IF,
    "then": THEN,
    "else": ELSE,
    "#": COMMENT,
    "for": FOR,
    "each": EACH,
    "in": IN,
    "check": CHECK,
    "equal": EQUAL,
    "less": LESS,
    "greater": GREATER,
    "than": THAN,
    "the": THE,
    "expecting": EXPECTING,
    "with": WITH,
    "while": WHILE,
    "not": NOT,
}

regex_tokens = {
    r"^\d+$": INTEGER,
    r'^"\w*"': STRING,
    r"^\w+$": VARNAME,
    r"^\d+\.\d+": FLOAT,
}
