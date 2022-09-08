Feature: Module name

  As a user of the dotmodules system,
  I want to name my configuration modules,
  So that I can find them easily.

  Dotmodules should automatically name the not explicitly named modules based on
  the directory the configuration file it is in.

  Background:
    Given I have the main modules directory at "./modules"
    And I set the dotmodules config file name as "dm.toml"

  Scenario: Missing module name should be inferred from the module directory
    Given I added an empty config file to "./module_1"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have its name set to "module_1"
    And there should be no module level errors

  Scenario: Missing module name should be inferred from the nested module directory
    Given I added an empty config file to "./category/module_1"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have its name set to "module_1"
    And there should be no module level errors

  Scenario: Explicitly named module should have the given name
    Given I added a config file to "./category/module" with content:
      name = "My module"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have its name set to "My module"
    And there should be no module level errors
