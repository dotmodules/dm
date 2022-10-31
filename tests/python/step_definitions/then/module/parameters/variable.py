import json

from pytest_bdd import then

from ....base import ExecutionContext, p


@then(p('the module at index "{index:I}" should have no variables'))
def assert_module_has_no_varibales(context: ExecutionContext, index: int) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.variables == {}


@then(
    p(
        'the module at index "{index:I}" should have the following variables:\n{json_lines:S}'
    )
)
def assert_module_has_specified_variables(
    context: ExecutionContext, index: int, json_lines: str
) -> None:
    variables = json.loads(json_lines)

    modules = context.modules
    module = modules[index - 1]
    assert module.variables == variables
