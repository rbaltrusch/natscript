# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:34 2020

@author: Korean_Crimson
"""
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


class TRUE(VALUE):
    def __init__(self, *_, **__):
        super().__init__(value=1)


class FALSE(VALUE):
    def __init__(self, *_, **__):
        super().__init__(value=0)


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

        value = self.TOKEN_FACTORY.create_value(run_tokens)
        interpreter.stack_append(value)


class FUNCTION(Token):
    def _run(self, interpreter):
        function = interpreter.stack_pop()
        code = interpreter.stack_pop()
        function.value = code.get_value()
        interpreter.set_variable(function.name, function)


class DEFINE(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((FUNCTION,), 3),
        ExpectedToken((VARNAME,), 2),
        ExpectedToken((AS,), 1),
        ExpectedToken((CLAUSE,), 0),
    ]


class CALL(Token):
    EXPECTED_TOKENS = [ExpectedToken((VARNAME,))]

    def _run(self, interpreter):
        function = interpreter.stack_pop()
        interpreter.add_stack()
        function.get_value()(interpreter)
        interpreter.remove_stack()


class THEN(Token):
    pass


class ELSE(Token):
    EXPECTED_TOKENS = [ExpectedToken((CLAUSE,))]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executed = False

    def _run(self, interpreter):
        else_clause = interpreter.stack_pop()
        value = interpreter.stack_pop()
        if value.get_value() == 0:
            else_clause.get_value()(interpreter)
            self.executed = True


class IF(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((THEN,), 1),
        ExpectedToken((CLAUSE,), 3),
        ExpectedToken((ELSE,), 2, optional=True),
    ]

    def _run(self, interpreter):
        if_clause = interpreter.stack_pop()
        if self.has_else:
            if not self.else_executed:
                if_clause.get_value()(interpreter)
        else:
            value = interpreter.stack_pop()
            if value.get_value() == 1:
                if_clause.get_value()(interpreter)

    @property
    def else_executed(self) -> bool:
        return self.has_else and self.tokens[-1].executed

    @property
    def has_else(self) -> bool:
        return isinstance(self.tokens[-1], ELSE)


class COLLECTION_R(Token):
    pass


class COLLECTION_L(VALUE, ClauseToken):

    CLOSE_TOKEN = COLLECTION_R

    def _run(self, interpreter):
        # ignore last token, which closes the collection (COLLECTION_R)
        self.value = [token.value for token in self.tokens][:-1]
        super()._run(interpreter)


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
    "[": COLLECTION_L,
    "]": COLLECTION_R,
    "define": DEFINE,
    "function": FUNCTION,
    "as": AS,
    "{": CLAUSE,
    "}": END,
    "call": CALL,
    "if": IF,
    "then": THEN,
    "else": ELSE,
    "#": COMMENT,
}

regex_tokens = {
    r"^\d+$": INTEGER,
    r"^\w+$": VARNAME,
    r"^\d+\.\d+": FLOAT,
}
