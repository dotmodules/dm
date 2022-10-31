Feature: Module enabled flag

  As a user of the dotmodules system,
  I want to add documentation to my modules,
  So that I can have a reference handy when I need it.

  Background:
    Given I have the main modules directory at "./modules"
    And I set the dotmodules config file name as "dm.toml"

  Scenario: Documentation is not mandatory
    Given I added an empty config file to "./module_1"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have empty documentation
    And there should be no module level errors

  Scenario: Documentation should be kept as is
    Given I added a config file to "./category/module" with content:
      documentation = """
      line 1
      line 2
        indented line 1
        indented line 2
      line 3
      """
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have its documentation set to:
      line 1
      line 2
        indented line 1
        indented line 2
      line 3
    And there should be no module level errors