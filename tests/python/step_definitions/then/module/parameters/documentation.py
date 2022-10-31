from pytest_bdd import then

from ....base import ExecutionContext, p


@then(p('the module at index "{index:I}" should have empty documentation'))
def assert_module_has_empty_documentation(
    context: ExecutionContext, index: int
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.documentation == []


@then(
    p(
        'the module at index "{index:I}" should have its documentation set to:\n{lines:S}'
    )
)
def assert_module_has_documentation_lines(
    context: ExecutionContext, index: int, lines: str
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert "\n".join(module.documentation) == lines
