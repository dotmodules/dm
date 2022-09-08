from pytest_bdd import then

from ..base import ExecutionContext, p


@then(p('the module at index "{index:I}" should have empty documentation'))
def assert_module_has_empty_documentation(
    execution_context: ExecutionContext, index: int
) -> None:
    modules = execution_context.modules
    module = modules[index - 1]
    assert module.documentation == []


@then(
    p(
        'the module at index "{index:I}" should have its documentation set to:\n{lines:S}'
    )
)
def assert_module_has_documentation_lines(
    execution_context: ExecutionContext, index: int, lines: str
) -> None:
    modules = execution_context.modules
    module = modules[index - 1]
    assert "\n".join(module.documentation) == lines
