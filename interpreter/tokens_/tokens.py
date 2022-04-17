# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:34 2020

@author: Korean_Crimson
"""
import operator
from typing import Optional

from interpreter.internal import exceptions
from interpreter.internal.interpreter import Interpreter
from interpreter.internal.token_ import ClauseToken
from interpreter.internal.token_ import ExpectedToken
from interpreter.internal.token_ import ExpectedTokenCombination
from interpreter.internal.token_ import SkipToken
from interpreter.internal.token_ import Token


# pylint: disable=no-self-use
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


class TO(Token):
    functional = False


class THAN(Token):
    functional = False


class FROM(Token):
    functional = False


class BY(Token):
    functional = False


class AS(Token):
    functional = False


class OF(Token):
    functional = False


class OUT(Token):
    functional = False


class THEN(Token):
    functional = False


class THE(SkipToken):
    pass


class THAT(SkipToken):
    pass


class IS(SkipToken):
    pass


class ARE(SkipToken):
    pass


class AND(SkipToken):
    pass

class COMMA(SkipToken):
    pass


class LINEBREAK(SkipToken):
    def update_token_factory(self, token_factory):
        token_factory.line_number += 1


class COMMENT(Token):
    def pop_tokens(self, tokens):
        popped_tokens = []
        while tokens:
            token = tokens.pop(0)
            popped_tokens.append(token)
            if isinstance(token, LINEBREAK):
                break
        return popped_tokens


class VALUE(Token):
    def _init(self, interpreter):
        self.token_value = self.TOKEN_FACTORY.create_value(self.value)

    def _run(self, interpreter):
        interpreter.stack_append(self.token_value)


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


class DEFAULTING(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((TO,), 0),
        ExpectedToken((VALUE,), 1)
    ]

    def _init(self, interpreter):
        for token in self.tokens:
            interpreter.run(token)

    def run(self, interpreter):
        pass


class VARNAME(VALUE):

    EXPECTED_TOKENS = [
        ExpectedToken((DEFAULTING,), optional=True)
    ]

    def _run(self, interpreter):
        try:
            variable = interpreter.get_variable(self.value)
        except exceptions.UndefinedVariableException:
            variable = self.TOKEN_FACTORY.create_variable(self.value)

        if self.has_all_optionals:
            default_value = interpreter.stack_pop()
            variable.value = default_value.get_value()
            interpreter.set_variable(variable.name, default_value)

        interpreter.stack_append(variable)
        interpreter.set_variable("it", variable)


class QualifierToken(Token):
    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        variable.add_qualifier(self.qualifier)
        interpreter.stack_append(variable)


QualifierToken.EXPECTED_TOKENS = [ExpectedToken((QualifierToken,), optional=True)]


class PRIVATE(QualifierToken):
    qualifier = "private"


class CONSTANT(QualifierToken):
    qualifier = "constant"

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        constant = self.TOKEN_FACTORY.create_constant(variable)
        interpreter.stack_append(constant)


class SET(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((QualifierToken), 3, optional=True),
        ExpectedToken((VARNAME,), 2),
        ExpectedToken((TO,), 1),
        ExpectedToken((VALUE,), 0),
    ]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = value.get_value()
        interpreter.set_variable(variable.name, variable)


class PRINT(Token):

    EXPECTED_TOKENS = [ExpectedToken((Token,))]

    def _run(self, interpreter):
        value = interpreter.stack_pop()
        print(value.get_value())


class ADD(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((TO,), 1),
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
        ExpectedToken((BY,), 1),
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


class CLAUSE_END(Token):
    pass


class CLAUSE(VALUE, ClauseToken):

    CLOSE_TOKEN = CLAUSE_END

    def _init(self, interpreter):
        self._none = self.TOKEN_FACTORY.create_none_value()
        self._runnable_tokens = self.tokens[:-1]

        for i, token in enumerate(self._runnable_tokens):
            if isinstance(token, RETURN):
                self._return_index = i
                break
        else:
            self._return_index = None

    def run(self, interpreter):
        value = self.TOKEN_FACTORY.create_value(self._run_tokens)
        interpreter.stack_append(value)

    def _run_tokens(self, interpreter):
        for i, token in enumerate(self._runnable_tokens):
            interpreter.run(token)
            if i == self._return_index:
                raise exceptions.ReturnException(self)
        else:
            interpreter.stack_append(self._none)


class FUNCTION(Token):
    def _run(self, interpreter):
        function = interpreter.stack_pop()
        code = interpreter.stack_pop()
        input_parameters = interpreter.stack_pop()
        function.value = code.get_value()
        function.inputs = input_parameters
        interpreter.set_variable(function.name, function)


class COLLECTION_END(Token):
    pass


class COLLECTION(VALUE, ClauseToken):

    CLOSE_TOKEN = COLLECTION_END

    def _init(self, interpreter):
        pass

    def _run(self, interpreter):
        # ignore last token, which closes the collection (COLLECTION_END)
        self.value = []
        for _ in self.tokens[:-1]:
            value = interpreter.stack_pop()
            self.value.append(value)
        self.value.reverse()
        value = self.TOKEN_FACTORY.create_iterable_value(self.value)
        interpreter.stack_append(value)


class APPEND(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((TO,), 1),
        ExpectedToken((VARNAME), 2)
    ]

    def _run(self, interpreter):
        collection = interpreter.stack_pop().get_value()
        value = interpreter.stack_pop().get_value()
        collection.append(value)


class REMOVE(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((FROM,), 1),
        ExpectedToken((VARNAME), 2)
    ]

    def _run(self, interpreter):
        collection = interpreter.stack_pop().get_value()
        value = interpreter.stack_pop().get_value()
        collection.remove(value)


class LENGTH(VALUE):

    EXPECTED_TOKENS = [
        ExpectedToken((OF,), 0),
        ExpectedToken((VALUE,), 1)
    ]

    def _run(self, interpreter):
        collection = interpreter.stack_pop().get_value()
        length = self.TOKEN_FACTORY.create_value(len(collection))
        interpreter.stack_append(length)


class EXPECTING(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((COLLECTION,), 0)
    ]

    def _run(self, interpreter):
        collection = interpreter.stack_pop()
        interpreter.stack_pop() # default empty args
        interpreter.stack_append(collection)


class WITH(Token):
    EXPECTED_TOKENS = [ExpectedToken((COLLECTION,), 0)]


class DEFINE(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((PRIVATE), 4, optional=True),
        ExpectedToken((FUNCTION,), 5),
        ExpectedToken((VARNAME,), 3),
        ExpectedToken((EXPECTING,), 0, optional=True),
        ExpectedToken((AS,), 2),
        ExpectedToken((CLAUSE,), 1),
    ]

    def run(self, interpreter):
        interpreter.stack_append(self.TOKEN_FACTORY.create_iterable_value(value=[]))
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

        if self.has_all_optionals:
            inputs = interpreter.stack_pop()
            inputs.get_value() #check defined
            input_values = inputs.value
        else:
            input_values = []

        interpreter.add_stack()
        # some functions dont have inputs

        if function.inputs and function.inputs.value:
            # take input parameters from stack
            for input_, variable in zip(input_values, function.inputs.value):
                variable.value = input_.get_value()
                variable.inputs = input_.inputs
                interpreter.set_variable(variable.name, variable)

        try:
            function.get_value()(interpreter)
        except exceptions.ReturnException:
            pass
        return_value = interpreter.stack_pop()
        interpreter.remove_stack()
        interpreter.set_variable('result', return_value)


class RESULT(VARNAME):
    EXPECTED_TOKENS = [
        ExpectedTokenCombination(
            ExpectedToken((OF,), 0),
            ExpectedToken((CALL,), 1),
            optional=True
        )
    ]

    def _run(self, interpreter):
        variable = interpreter.get_variable("result")
        interpreter.remove_variable("result")
        interpreter.set_variable("it", variable)
        interpreter.stack_append(variable)


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
    EXPECTED_TOKENS = [ExpectedToken((VALUE,))]

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
        ExpectedToken((VALUE, CHECK), 1),
        ExpectedToken((THEN,), 2),
        ExpectedToken((CLAUSE,), 3),
        ExpectedToken((ELSE,), 0, optional=True),
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


class IN(Token):
    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = value.get_value()
        interpreter.set_variable(variable.name, variable)


class EACH(Token):

    # run order is ignored by EACH.run method
    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 1),
        ExpectedToken((IN,), 2),
        ExpectedToken((VALUE,), 0),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = 0
        self.collection = None

    def run(self, interpreter):
        if self.collection is None:
            interpreter.run(self.tokens[-1])
            self.collection = interpreter.stack_pop().get_value()

        if self.exhausted:
            return

        value = self.TOKEN_FACTORY.create_any_value(
            value=self.collection[self._index]
        )
        interpreter.stack_append(value)
        self._index += 1

        # ignore collection (last token), as it was previously run
        for token in self.tokens[:-1]:
            interpreter.run(token)

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
                interpreter.run(token)
            clause = interpreter.stack_pop()
            try:
                if self._check_condition(interpreter):
                    clause.get_value()(interpreter)
            except exceptions.SkipElementException:
                pass
            except exceptions.BreakIterationException:
                break
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
        interpreter.run(self.tokens[-1])
        clause_function = interpreter.stack_pop().get_value()
        condition = self.tokens[0]
        while True:
            condition.run(interpreter)
            if not interpreter.stack_pop().get_value():
                break

            try:
                clause_function(interpreter)
            except exceptions.BreakIterationException:
                break


class GREATER(CONDITION):
    OPERATOR = operator.gt
    EXPECTED_TOKENS = [
        ExpectedToken((THAN,), 0),
        ExpectedToken((VALUE,), 1),
    ]

class EQUAL(CONDITION):
    OPERATOR = operator.eq
    EXPECTED_TOKENS = [
        ExpectedToken((TO,), 0),
        ExpectedToken((VALUE,), 1),
    ]

class LESS(CONDITION):
    OPERATOR = operator.lt
    EXPECTED_TOKENS = [
        ExpectedToken((THAN,), 0),
        ExpectedToken((VALUE,), 1),
    ]


class FIRST(VALUE):

    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 1),
        ExpectedToken((IN,), 2),
        ExpectedToken((VALUE,), 0),
    ]
    RETURN_TOKEN_INDEX = 0

    def run(self, interpreter):
        interpreter.run(self.tokens[-1])
        collection = interpreter.stack_pop().get_value()

        value = self.TOKEN_FACTORY.create_any_value(
            value=collection[self.RETURN_TOKEN_INDEX]
        )
        interpreter.stack_append(value)
        # ignore collection (last token), as it was previously run
        for token in self.tokens[:-1]:
            interpreter.run(token)

        # append it again, previous stack append gets consumed by IN token
        interpreter.stack_append(value)


class LAST(FIRST):
    RETURN_TOKEN_INDEX = -1


class ROUND(VALUE):
    EXPECTED_TOKENS = [ExpectedToken((VALUE,))]

    def _run(self, interpreter):
        value = interpreter.stack_pop()
        value.value = round(value.value)
        interpreter.stack_append(value)


class ANY_CHARACTER(Token):
    def _run(self, interpreter):
        raise exceptions.SyntaxException(self) from None


class AT(Token):
    EXPECTED_TOKENS = [ExpectedToken((VALUE,))]


class GET(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME), 3),
        ExpectedToken((FROM,), 1),
        ExpectedToken((VALUE), 2),
        ExpectedToken((AT,), 0),
    ]

    def _run(self, interpreter):
        variable = interpreter.stack_pop()
        collection = interpreter.stack_pop().get_value()
        index = interpreter.stack_pop().get_value()
        variable.value = collection[index]


class CollectionLogicToken(VALUE):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((CONDITION,), 1, optional=True),
    ]
    initial_condition_value = True

    def run(self, interpreter):
        interpreter.run(self.tokens[0])
        collection = interpreter.stack_pop().get_value()

        for value in collection:
            result = self._get_condition_result(value, interpreter)
            if self._check_if_should_break(result):
                condition_value = not self.initial_condition_value
                break
        else:
            condition_value = self.initial_condition_value

        result = self.TOKEN_FACTORY.create_value(condition_value)
        interpreter.stack_append(result)

    def _get_condition_result(self, value, interpreter):
        if not self.has_all_optionals:
            return bool(value)

        interpreter.stack_append(self.TOKEN_FACTORY.create_any_value(value))
        interpreter.run(self.tokens[1])
        return interpreter.stack_pop().get_value()


class ALL(CollectionLogicToken):

    initial_condition_value = True

    def _check_if_should_break(self, result):
        return not result


class ANY(CollectionLogicToken):

    initial_condition_value = False

    def _check_if_should_break(self, result):
        return result


class SOME(CollectionLogicToken):

    initial_condition_value = False

    def run(self, interpreter):
        self.counter = 0
        super().run(interpreter)

    def _check_if_should_break(self, result):
        if result:
            self.counter += 1
        return self.counter > 1


class NONE(CollectionLogicToken):

    initial_condition_value = True

    def _check_if_should_break(self, result):
        return result


class IMPORT(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((COLLECTION,), 2),
        ExpectedToken((FROM,), 1),
        ExpectedToken((STRING,), 0),
    ]

    def run(self, interpreter):
        interpreter.run(self.tokens[0])
        import_variables = interpreter.stack_pop().value
        filename = self.tokens[-1].value

        from interpreter import interpret
        tokens = interpret.construct_tokens(filename)

        interpreter.add_stack()
        for token in tokens:
            interpreter.init(token)

        for token in tokens:
            interpreter.run(token)

        variables = []
        for import_variable in import_variables:
            variable = interpreter.get_variable(import_variable.name)
            if variable.get_qualifier("private"):
                raise exceptions.ImportException(
                    f"Could not import private variable {variable.name} from module {filename}!",
                    token=self,
                ) from None
            variables.append(variable)
        interpreter.remove_stack()

        for variable in variables:
            interpreter.set_variable(variable.name, variable)


class SKIP(Token):
    EXPECTED_TOKENS = [ExpectedToken((VARNAME,), optional=True)]

    def _run(self, interpreter):
        raise exceptions.SkipElementException(self)


class BREAK(Token):
    EXPECTED_TOKENS = [ExpectedToken((OUT,))]

    def _run(self, interpreter):
        raise exceptions.BreakIterationException(self)


class RANGE(VALUE):

    EXPECTED_TOKENS = [
        ExpectedToken((FROM,), 0),
        ExpectedToken((VALUE,), 1),
        ExpectedToken((TO,), 2),
        ExpectedToken((VALUE,), 3),
    ]

    def _run(self, interpreter):
        end = interpreter.stack_pop().get_value()
        start = interpreter.stack_pop().get_value()
        interpreter.stack_append(
            self.TOKEN_FACTORY.create_iterable_value(value=list(range(start, end)))
        )

def get_tokens():
    return {
        "set": SET,
        "to": TO,
        "defaulting": DEFAULTING,
        "from": FROM,
        "by": BY,
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
        "}": CLAUSE_END,
        "return": RETURN,
        "nothing": NOTHING,
        "result": RESULT,
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
        "first": FIRST,
        "last": LAST,
        "length": LENGTH,
        "of": OF,
        "append": APPEND,
        "remove": REMOVE,
        "round": ROUND,
        "get": GET,
        "at": AT,
        "is": IS,
        "that": THAT,
        "are": ARE,
        "all": ALL,
        "any": ANY,
        "some": SOME,
        "none": NONE,
        "import": IMPORT,
        "skip": SKIP,
        "break": BREAK,
        "out": OUT,
        "private": PRIVATE,
        "constant": CONSTANT,
        "range": RANGE,
    }


def get_regex_tokens():
    return {
        r"^\d+$": INTEGER,
        r'^".*"': STRING,
        r"^\w+$": VARNAME,
        r"^\d+\.\d+": FLOAT,
        r".": ANY_CHARACTER,
    }
