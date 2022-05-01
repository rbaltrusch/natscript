# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 13:54:34 2020

@author: Korean_Crimson
"""
# #pylint: disable=too-many-lines

import codecs
import importlib
import operator
import os
from typing import Any, List

from interpreter.internal import exceptions
from interpreter.internal.interfaces import Interpreter, Value, Variable
from interpreter.internal.token_ import (
    ClauseToken,
    ExpectedToken,
    ExpectedTokenCombination,
    SkipToken,
    Token,
)

# type: ignore
# pylint: disable=invalid-name
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
    def _init(self, interpreter: Interpreter):
        # pylint: disable=attribute-defined-outside-init
        self.token_value = self.TOKEN_FACTORY.create_value(self.value)

    def _run(self, interpreter: Interpreter):
        interpreter.stack_append(self.token_value)


class INTEGER(VALUE):
    def _convert_value(self, value):
        return int(value)


class FLOAT(VALUE):
    def _convert_value(self, value):
        return float(value)


class STRING(VALUE):
    def _convert_value(self, value):
        string_ = str(value.strip('"'))
        return codecs.decode(string_, "unicode_escape")


class TRUE(VALUE):
    def __init__(self, *_, **__):
        super().__init__(value=True)


class FALSE(VALUE):
    def __init__(self, *_, **__):
        super().__init__(value=False)


class NOTHING(VALUE):
    def _convert_value(self, value):
        return None

    def _init(self, interpreter: Interpreter):
        # pylint: disable=attribute-defined-outside-init
        self.token_value = self.TOKEN_FACTORY.create_none_value()


class DEFAULTING(Token):
    must_be_subtoken = True
    EXPECTED_TOKENS = [ExpectedToken((TO,), 0), ExpectedToken((VALUE,), 1)]

    def run(self, interpreter: Interpreter):
        for token in self.tokens:
            interpreter.run(token)


class VARNAME(VALUE):

    EXPECTED_TOKENS = [ExpectedToken((DEFAULTING,), optional=True)]

    def _run(self, interpreter: Interpreter):
        try:
            variable = interpreter.get_variable(self.value)
        except exceptions.UndefinedVariableException:
            variable = self.TOKEN_FACTORY.create_variable(self.value)

        if self.has_all_optionals:
            default_value = interpreter.stack_pop()
            variable.value = default_value.get_value()
            interpreter.set_variable(variable.name, variable)

        interpreter.stack_append(variable)
        interpreter.set_variable("it", variable)


class QualifierToken(Token):
    must_be_subtoken = True

    def _run(self, interpreter: Interpreter):
        variable = interpreter.stack_pop()
        variable.add_qualifier(self.qualifier)  # pylint: disable=no-member
        interpreter.stack_append(variable)


QualifierToken.EXPECTED_TOKENS = [ExpectedToken((QualifierToken,), optional=True)]


class PRIVATE(QualifierToken):
    qualifier = "private"


class CONSTANT(QualifierToken):
    qualifier = "constant"

    def _run(self, interpreter: Interpreter):
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

    def _run(self, interpreter: Interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        variable.value = value.get_value()
        interpreter.set_variable(variable.name, variable)


class PRINT(Token):

    EXPECTED_TOKENS = [ExpectedToken((Token,))]

    def _run(self, interpreter: Interpreter):
        value = interpreter.stack_pop()
        print(value.convert_to_str())


class OperatorToken(Token):
    def _run(self, interpreter: Interpreter):
        variable = interpreter.stack_pop()
        value = interpreter.stack_pop()
        try:
            self.do_operation(variable, value)  # pylint: disable=no-member
        except TypeError:
            type_ = lambda x: x.get_value().__class__.__name__
            raise exceptions.TypeException(
                f"Unsupported operation for types {type_(variable)} and {type_(value)}!",
                token=self,
            ) from None


class ADD(OperatorToken):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((TO,), 1),
        ExpectedToken((VARNAME,), 2),
    ]

    def do_operation(self, variable: Variable, value: Value) -> None:
        variable.value = variable.get_value() + value.get_value()


class SUBTRACT(OperatorToken):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((FROM,), 1),
        ExpectedToken((VARNAME,), 2),
    ]

    def do_operation(self, variable: Variable, value: Value) -> None:
        variable.value = variable.get_value() - value.get_value()


class MULTIPLY(OperatorToken):

    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 2),
        ExpectedToken((BY,), 1),
        ExpectedToken((VALUE,), 0),
    ]

    def do_operation(self, variable: Variable, value: Value) -> None:
        variable.value = variable.get_value() * value.get_value()


class DIVIDE(OperatorToken):

    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 2),
        ExpectedToken((BY,), 1),
        ExpectedToken((VALUE,), 0),
    ]

    def do_operation(self, variable: Variable, value: Value) -> None:
        variable.value = variable.get_value() / value.get_value()
        if variable.value == int(variable.value):
            variable.value = int(variable.value)


class IT(VARNAME):
    def _run(self, interpreter: Interpreter):
        variable = interpreter.get_variable("it")
        interpreter.stack_append(variable)


class CLAUSE_END(Token):
    pass


class CLAUSE(VALUE, ClauseToken):

    CLOSE_TOKEN = CLAUSE_END

    def _init(self, interpreter: Interpreter):
        # pylint: disable=attribute-defined-outside-init
        self._none = self.TOKEN_FACTORY.create_none_value()
        self._runnable_tokens = self.tokens[:-1]

    def run(self, interpreter: Interpreter):
        value = self.TOKEN_FACTORY.create_value(self._run_tokens)
        interpreter.stack_append(value)

    def _run_tokens(self, interpreter: Interpreter):
        for token in self._runnable_tokens:
            interpreter.run(token)
        interpreter.stack_append(self._none)


class FUNCTION(Token):
    must_be_subtoken = True

    def _run(self, interpreter: Interpreter):
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

    def _init(self, interpreter: Interpreter):
        pass

    def _run(self, interpreter: Interpreter):
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
        ExpectedToken((VARNAME), 2),
    ]

    def _run(self, interpreter: Interpreter):
        collection_variable = interpreter.stack_pop()
        collection: List[Any] = collection_variable.get_value()
        value = interpreter.stack_pop().get_value()

        try:
            collection.append(value)
        except AttributeError:
            raise exceptions.TypeException(
                f"Cannot append value to type {collection.__class__.__name__}!",
                token=self,
            ) from None


class POP(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 2),
        ExpectedToken((FROM,), 1),
        ExpectedToken((VARNAME), 0),
    ]

    def _run(self, interpreter: Interpreter):
        variable = interpreter.stack_pop()
        collection_variable: List[Any] = interpreter.stack_pop()
        collection = collection_variable.get_value()

        try:
            variable.value = collection.pop()
        except AttributeError:
            raise exceptions.TypeException(
                f"Cannot pop from type {collection.__class__.__name__}!", token=self
            ) from None
        except IndexError:
            raise exceptions.ValueException(
                "Cannot pop from empty collection!", token=self
            ) from None

        interpreter.set_variable(variable.name, variable)


class REMOVE(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((FROM,), 1),
        ExpectedToken((VARNAME), 2),
    ]

    def _run(self, interpreter: Interpreter):
        collection: List[Any] = interpreter.stack_pop().get_value()
        value = interpreter.stack_pop().get_value()

        try:
            collection.remove(value)
        except AttributeError:
            raise exceptions.TypeException(
                f"Cannot remove value from type {collection.__class__.__name__}!",
                token=self,
            ) from None
        except ValueError:
            raise exceptions.ValueException(
                "Value not in collection!", token=self
            ) from None


class LENGTH(VALUE):

    EXPECTED_TOKENS = [ExpectedToken((OF,), 0), ExpectedToken((VALUE,), 1)]

    def _run(self, interpreter: Interpreter):
        collection = interpreter.stack_pop().get_value()

        try:
            len_ = len(collection)
        except TypeError:
            raise exceptions.TypeException(
                f"Value of type {collection.__class__.__name__} has no length!",
                token=self,
            ) from None

        length = self.TOKEN_FACTORY.create_value(len_)
        interpreter.stack_append(length)


class EXPECTING(Token):
    must_be_subtoken = True
    EXPECTED_TOKENS = [ExpectedToken((COLLECTION,), 0)]

    def _run(self, interpreter: Interpreter):
        collection = interpreter.stack_pop()
        interpreter.stack_pop()  # default empty args
        interpreter.stack_append(collection)


class WITH(Token):
    must_be_subtoken = True
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

    def run(self, interpreter: Interpreter):
        interpreter.stack_append(self.TOKEN_FACTORY.create_iterable_value(value=[]))
        super().run(interpreter)


class RETURN(Token):
    EXPECTED_TOKENS = [ExpectedToken((VALUE,), 0)]

    def _run(self, interpreter: Interpreter):
        raise exceptions.ReturnException(self)


class CALL(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME, CLAUSE), 1),
        ExpectedToken((WITH,), 0, optional=True),
    ]

    def _run(self, interpreter: Interpreter):
        function = interpreter.stack_pop()

        input_values: List[Any]
        if self.has_all_optionals:
            inputs = interpreter.stack_pop()
            inputs.get_value()  # check defined
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
        except TypeError:
            raise exceptions.TypeException(
                f"Cannot call variable of type {function.get_value().__class__.__name__}!",
                token=self,
            ) from None
        except exceptions.ReturnException:
            pass
        return_value: Variable = interpreter.stack_pop()  # type: ignore
        interpreter.remove_stack()
        interpreter.set_variable("result", return_value)


class RESULT(VARNAME):
    EXPECTED_TOKENS = [
        ExpectedTokenCombination(
            ExpectedToken((OF,), 0), ExpectedToken((CALL,), 1), optional=True
        )
    ]

    def _run(self, interpreter: Interpreter):
        variable = interpreter.get_variable("result")
        interpreter.remove_variable("result")
        interpreter.set_variable("it", variable)
        interpreter.stack_append(variable)


class ELSE(Token):
    must_be_subtoken = True
    EXPECTED_TOKENS = [ExpectedToken((CLAUSE,))]


class CONDITION(VALUE, ClauseToken):

    OPERATOR = operator.eq
    CLOSE_TOKEN = VALUE

    def _run(self, interpreter: Interpreter):
        second_value = interpreter.stack_pop().get_value()
        first_value = interpreter.stack_pop().get_value()
        condition_result = self.OPERATOR(  # pylint: disable=too-many-function-args
            first_value, second_value
        )
        value = self.TOKEN_FACTORY.create_value(condition_result)
        interpreter.stack_append(value)


class NOT(CONDITION):
    EXPECTED_TOKENS = [ExpectedToken((VALUE,))]

    def _run(self, interpreter: Interpreter):
        value = interpreter.stack_pop()
        value.negate_value()
        interpreter.stack_append(value)


class CHECK(VALUE):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((CONDITION,), 1),
    ]

    def _run(self, interpreter: Interpreter):
        pass


class IF(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((VALUE, CHECK), 1),
        ExpectedToken((THEN,), 2),
        ExpectedToken((CLAUSE,), 3),
        ExpectedToken((ELSE,), 0, optional=True),
    ]

    def _run(self, interpreter: Interpreter):
        if_clause = interpreter.stack_pop()
        condition_value = interpreter.stack_pop()
        else_clause = interpreter.stack_pop() if self.has_all_optionals else None
        if condition_value.get_value() == 1:
            if_clause.get_value()(interpreter)
        elif else_clause is not None:
            else_clause.get_value()(interpreter)


class IN(Token):
    must_be_subtoken = True

    def _run(self, interpreter: Interpreter):
        variable: Variable = interpreter.stack_pop()  # type: ignore
        value = interpreter.stack_pop()
        variable.value = value.get_value()
        interpreter.set_variable(variable.name, variable)


class EACH(Token):
    must_be_subtoken = True

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

    def run(self, interpreter: Interpreter):
        if self.collection is None:
            interpreter.run(self.tokens[-1])
            self.collection = interpreter.stack_pop().get_value()

        try:
            collection_value = self.collection[self._index]
        except IndexError:
            self.reset()
            raise exceptions.BreakIterationException(self) from None
        except TypeError:
            raise exceptions.TypeException(
                f"Cannot iterate through value of type {self.collection.__class__.__name__}!",
                token=self,
            ) from None

        value = self.TOKEN_FACTORY.create_any_value(value=collection_value)
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


class FOR(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((EACH,), 0),
        ExpectedToken((CONDITION,), 1, optional=True),
        ExpectedToken((CLAUSE,), 2),
    ]

    def run(self, interpreter: Interpreter):
        while True:
            try:
                for token in self.tokens:
                    interpreter.run(token)
            except exceptions.BreakIterationException:
                break

            clause = interpreter.stack_pop()
            try:
                if self._check_condition(interpreter):
                    clause.get_value()(interpreter)
            except exceptions.SkipElementException:
                pass
            except exceptions.BreakIterationException:
                break

    def _check_condition(self, interpreter: Interpreter) -> bool:
        value = interpreter.stack_pop()
        if not self.has_all_optionals:
            return True
        return value.get_value()


class WHILE(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((CLAUSE,), 1),
    ]

    def run(self, interpreter: Interpreter):
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


class CONTAINS(CONDITION):
    OPERATOR = operator.contains
    EXPECTED_TOKENS = [ExpectedToken((VALUE,))]


class IDENTICAL(CONDITION):
    OPERATOR = operator.is_
    EXPECTED_TOKENS = [
        ExpectedToken((TO,), 0),
        ExpectedToken((VALUE,), 1),
    ]


class FIRST(VALUE):

    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 1),
        ExpectedToken((IN,), 2),
        ExpectedToken((VALUE,), 0),
    ]
    RETURN_TOKEN_INDEX = 0

    def run(self, interpreter: Interpreter):
        interpreter.run(self.tokens[-1])
        collection = interpreter.stack_pop().get_value()

        try:
            collection_value = collection[self.RETURN_TOKEN_INDEX]
        except IndexError:
            raise exceptions.ValueException(
                "Cannot extract value from empty collection!"
            ) from None
        except TypeError:
            raise exceptions.TypeException(
                f"Cannot extract from value of type {collection.__class__.__name__}!",
            ) from None

        value = self.TOKEN_FACTORY.create_any_value(collection_value)
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

    def _run(self, interpreter: Interpreter):
        value = interpreter.stack_pop()
        try:
            value.value = round(value.value)
        except TypeError:
            raise exceptions.TypeException(
                f"Cannot round value of type {value.value.__class__.__name__}!"
            ) from None


class ANY_CHARACTER(Token):
    def _run(self, interpreter: Interpreter):
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

    def _run(self, interpreter: Interpreter):
        variable = interpreter.stack_pop()
        collection = interpreter.stack_pop().get_value()
        index = interpreter.stack_pop().get_value()

        try:
            variable.value = collection[index]
        except IndexError:
            raise exceptions.ValueException(
                f"Collection index {index} out of range!"
            ) from None
        except TypeError:
            raise exceptions.TypeException(
                f"Cannot index value of type {collection.__class__.__name__}!"
            ) from None

        interpreter.set_variable(variable.name, variable)


class UPDATE(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME,), 2),
        ExpectedToken((AT,), 3),
        ExpectedToken((TO,), 1),
        ExpectedToken((VALUE,), 0),
    ]

    def _run(self, interpreter: Interpreter):
        index = interpreter.stack_pop().get_value()
        parent_value = interpreter.stack_pop().get_value()
        value = interpreter.stack_pop()
        try:
            parent_value[index] = value.get_value()
        except TypeError:
            raise exceptions.TypeException(
                f"Value of type {parent_value.__class__.__name__} cannot be indexed!"
            ) from None
        except IndexError:
            raise exceptions.ValueException("Index out of range!") from None


class CollectionLogicToken(VALUE):

    EXPECTED_TOKENS = [
        ExpectedToken((VALUE,), 0),
        ExpectedToken((CONDITION,), 1, optional=True),
    ]
    initial_condition_value = True

    def run(self, interpreter: Interpreter):
        interpreter.run(self.tokens[0])
        collection = interpreter.stack_pop().get_value()

        for value in collection:
            result = self._get_condition_result(value, interpreter)
            if self._check_if_should_break(result):  # pylint: disable=no-member
                condition_value = not self.initial_condition_value
                break
        else:
            condition_value = self.initial_condition_value

        result = self.TOKEN_FACTORY.create_value(condition_value)
        interpreter.stack_append(result)

    def _get_condition_result(self, value: Any, interpreter: Interpreter) -> bool:
        if not self.has_all_optionals:
            return bool(value)

        interpreter.stack_append(self.TOKEN_FACTORY.create_any_value(value))
        interpreter.run(self.tokens[1])  # type: ignore
        return interpreter.stack_pop().get_value()


class ALL(CollectionLogicToken):

    initial_condition_value = True

    def _check_if_should_break(self, result: bool):
        return not result


class ANY(CollectionLogicToken):

    initial_condition_value = False

    def _check_if_should_break(self, result: bool):
        return result


class SOME(CollectionLogicToken):

    initial_condition_value = False

    def run(self, interpreter: Interpreter):
        self.counter = 0  # pylint: disable=attribute-defined-outside-init
        super().run(interpreter)

    def _check_if_should_break(self, result: bool):
        if result:
            self.counter += 1
        return self.counter > 1


class NONE(CollectionLogicToken):

    initial_condition_value = True

    def _check_if_should_break(self, result: bool):
        return result


class IMPORT(Token):

    EXPECTED_TOKENS = [
        ExpectedToken((COLLECTION,), 2),
        ExpectedToken((FROM,), 1),
        ExpectedToken((STRING,), 0),
    ]

    def run(self, interpreter: Interpreter):
        interpreter.run(self.tokens[0])
        import_variables = interpreter.stack_pop().value
        filename = self.tokens[-1].value

        import_ = (
            self._import_python_module
            if filename.endswith(".py")
            else self._import_tokens
        )
        try:
            import_(interpreter, filename)
        except (FileNotFoundError, ModuleNotFoundError):
            raise exceptions.ImportException(
                f"Failed to import because file could not be found: {filename}",
                token=self,
            ) from None

        variables: List[Variable] = []
        for import_variable in import_variables:

            try:
                variable = interpreter.get_variable(import_variable.name)
            except AttributeError:
                type_ = import_variable.value.__class__.__name__
                raise exceptions.ValueException(
                    f"Cannot import: value of type {type_} is not a variable!"
                ) from None

            if variable.get_qualifier("private"):
                raise exceptions.ImportException(
                    f"Could not import private variable {variable.name} from module {filename}!",
                    token=self,
                ) from None
            variables.append(variable)
        interpreter.remove_stack()

        for variable in variables:
            interpreter.set_variable(variable.name, variable)

    def _import_tokens(self, interpreter: Interpreter, filename: str) -> None:
        from interpreter import interpret

        tokens = interpret.construct_tokens(filename)
        interpreter.add_stack()
        for token in tokens:
            interpreter.init(token)

        for token in tokens:
            interpreter.run(token)

    def _import_python_module(self, interpreter: Interpreter, filename: str) -> None:
        module = importlib.import_module(os.path.splitext(filename)[0])
        interpreter.add_stack()
        for name, value in module.__dict__.items():
            if name.startswith("_"):
                continue

            variable = self.TOKEN_FACTORY.create_variable(name)
            if callable(value):
                variable.inputs = self.TOKEN_FACTORY.create_iterable_value(
                    value=[
                        self.TOKEN_FACTORY.create_variable(x)
                        for x in range(value.__code__.co_argcount)
                    ]
                )
                value = self._wrap_python_callable(value)
            variable.value = value
            interpreter.set_variable(name, variable)
            interpreter.set_variable("it", variable)

    def _wrap_python_callable(self, function):
        def inner(interpreter: Interpreter):
            args = []
            for x in range(function.__code__.co_argcount):
                try:
                    args.append(interpreter.get_variable(x).get_value())
                except exceptions.UndefinedVariableException:
                    break

            try:
                return_value = function(*args)
            except TypeError as exc:
                raise exceptions.RunTimeException(token=self) from exc
            interpreter.stack_append(self.TOKEN_FACTORY.create_any_value(return_value))

        return inner


class SKIP(Token):
    EXPECTED_TOKENS = [ExpectedToken((VARNAME,), optional=True)]

    def _run(self, interpreter: Interpreter):
        raise exceptions.SkipElementException(self)


class BREAK(Token):
    EXPECTED_TOKENS = [ExpectedToken((OUT,))]

    def _run(self, interpreter: Interpreter):
        raise exceptions.BreakIterationException(self)


class RANGE(VALUE):

    EXPECTED_TOKENS = [
        ExpectedToken((FROM,), 0),
        ExpectedToken((VALUE,), 1),
        ExpectedToken((TO,), 2),
        ExpectedToken((VALUE,), 3),
    ]

    def _run(self, interpreter: Interpreter):
        end = interpreter.stack_pop().get_value()
        start = interpreter.stack_pop().get_value()
        interpreter.stack_append(
            self.TOKEN_FACTORY.create_iterable_value(value=list(range(start, end)))
        )


class EXIT(Token):
    EXPECTED_TOKENS = [ExpectedToken((VALUE,), optional=True)]

    def _run(self, interpreter: Interpreter):
        values = interpreter.stack_pop().get_value() if self.has_all_optionals else []
        raise SystemExit(*values)


class SLICE(VALUE):
    EXPECTED_TOKENS = [
        ExpectedToken((OF,), 0),
        ExpectedToken((VALUE,), 4),
        ExpectedToken((FROM,), 1),
        ExpectedToken((VALUE,), 2),
        ExpectedToken((TO,), 3),
        ExpectedToken((VALUE,), 5),
    ]

    def _run(self, interpreter: Interpreter):
        end_index = interpreter.stack_pop().get_value()
        collection = interpreter.stack_pop().get_value()
        start_index = interpreter.stack_pop().get_value()
        if not isinstance(start_index, int):
            raise exceptions.ValueException(
                f"Wrong index of type {start_index.__class__.__name__}!"
            ) from None

        try:
            subcollection = collection[start_index:end_index]
        except TypeError:
            raise exceptions.TypeException(
                f"Value of type {collection.__class__.__name__} cannot be indexed!"
            ) from None
        except IndexError:
            raise exceptions.ValueException("Index out of range!") from None

        interpreter.stack_append(
            self.TOKEN_FACTORY.create_iterable_value(subcollection)
        )


class END(VALUE):
    def _run(self, interpreter: Interpreter):
        try:
            collection = interpreter.stack_pop()
        except exceptions.EmptyStackError:
            self.raise_syntax_exception()

        interpreter.stack_append(collection)

        try:
            len_ = len(collection.get_value())
        except TypeError:
            raise exceptions.TypeException(
                f"Value of type {collection.__class__.__name__} has no length!"
            ) from None

        interpreter.stack_append(self.TOKEN_FACTORY.create_value(len_))


class APPLY(Token):
    EXPECTED_TOKENS = [
        ExpectedToken((VARNAME), 0),
        ExpectedToken((TO,), 1),
        ExpectedToken((VALUE,), 2),
    ]

    def _run(self, interpreter: Interpreter):
        collection = interpreter.stack_pop()
        try:
            list_ = list(collection.get_value())
        except TypeError:
            raise exceptions.TypeException(
                f"Value of type {collection.get_value().__class__.__name__} is not iterable!"
            ) from None

        function = interpreter.stack_pop()
        # some functions dont have inputs
        if (
            not function.inputs
            or not function.inputs.value
            or not len(function.inputs.value) == 1
        ):
            raise exceptions.TypeException("Apply function should expect one input!")

        interpreter.add_stack()
        variable = function.inputs.value[0]
        interpreter.set_variable(variable.name, variable)
        for i, value in enumerate(list_):
            variable.value = value
            try:
                function.get_value()(interpreter)
            except TypeError:
                raise exceptions.TypeException(
                    f"Cannot call variable of type {function.get_value().__class__.__name__}!"
                ) from None
            except exceptions.ReturnException:
                pass
            collection.value[i] = interpreter.stack_pop().get_value()  # return value
        interpreter.remove_stack()


class REVERSE(Token):
    EXPECTED_TOKENS = [ExpectedToken((VALUE,))]

    def _run(self, interpreter: Interpreter):
        collection: List[Any] = interpreter.stack_pop().get_value()
        try:
            collection.reverse()
        except AttributeError:
            raise exceptions.TypeException(
                f"Cannot reverse value of type {collection.__class__.__name__}!"
            ) from None


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
        "checked": CHECK,
        "equal": EQUAL,
        "less": LESS,
        "greater": GREATER,
        "than": THAN,
        "contains": CONTAINS,
        "identical": IDENTICAL,
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
        "pop": POP,
        "round": ROUND,
        "update": UPDATE,
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
        "itself": IT,
        "exit": EXIT,
        "slice": SLICE,
        "end": END,
        "apply": APPLY,
        "reverse": REVERSE,
    }


def get_regex_tokens():
    return {
        r"^[-]*\d+$": INTEGER,
        r'^".*"': STRING,
        r"^\w+$": VARNAME,
        r"^\d+\.\d+": FLOAT,
        r".": ANY_CHARACTER,
    }
