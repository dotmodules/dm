Feature: Module variables

  As a user of the dotmodules system,
  I want to set varibales for my modules,
  So that I can integrate them into other modules in a decoupled way.

  A module can set multiple values (value) to a variable name (key) like a
  dictionary that contains a list of strings as a specialized key-value store.
  Variables will be aggregated from the enabled modules at loading time and will
  be made available publicly for the individual modules.

  In this way the variables provides a way to communicate between modules.

  Background:
    Given I have the main modules directory at "./modules"
    And I set the dotmodules config file name as "dm.toml"

  Scenario: Empty variables should be tolerated
    Given I added an empty config file to "./module_1"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have no variables
    And there should be no module level errors

  Scenario: Variables should be specified with a single value
    Given I added a config file to "./category/module" with content:
      [variables]
      VARIABLE = "value"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have the following variables:
      {
        "VARIABLE": ["value"]
      }
    And there should be no module level errors

  Scenario: Variables should be specified with a multiple values
    Given I added a config file to "./category/module" with content:
      [variables]
      VARIABLE = ["value_1", "value_2"]
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have the following variables:
      {
        "VARIABLE": ["value_1", "value_2"]
      }
    And there should be no module level errors

  Scenario: Variables can have multiple values
    Given I added a config file to "./category/module" with content:
      [variables]
      VARIABLE = "value_1"
      VARIABLE = "value_2"
    When I run the dotmodules system
    Then there should be no modules loaded
    And a global error should have been raised:
      Duplicate keys!
