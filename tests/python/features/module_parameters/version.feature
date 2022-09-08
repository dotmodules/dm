Feature: Module version

  As a user of the dotmodules system,
  I want to have version numbers associated with the modules,
  So that I can use and identify third party modules as well.

  Dotmodules should ignore if the version is not specified.

  Background:
    Given I have the main modules directory at "./modules"
    And I set the dotmodules config file name as "dm.toml"

  Scenario: Missing module version should have a default value
    Given I added an empty config file to "./module_1"
    When I run the dotmodules system
    Then the module at index "1" should have its version set to "-"
    And there should be no module level errors

  Scenario: Explicitly versioned module should persist the version
    Given I added a config file to "./category/module" with content:
      version = "v1.0.0"
    When I run the dotmodules system
    Then the module at index "1" should have its version set to "v1.0.0"
    And there should be no module level errors
