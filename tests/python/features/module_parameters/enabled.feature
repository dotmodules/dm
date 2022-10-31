Feature: Module enabled flag

  As a user of the dotmodules system,
  I want to flag modules as disabled,
  So that I can specify what modules to be loaded.

  Modules are enabled by default, disabling them should be explicit.

  Background:
    Given I have the main modules directory at "./modules"
    And I set the dotmodules config file name as "dm.toml"

  Scenario: Missing enabled flag means the module is enabled
    Given I added an empty config file to "./module_1"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should be enabled
    And there should be no module level errors

  Scenario: Modules can be enabled explicitly
    Given I added a config file to "./category/module" with content:
      enabled = true
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should be enabled
    And there should be no module level errors

  Scenario: Modules can only be disabled explicitly
    Given I added a config file to "./category/module" with content:
      enabled = false
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should be disabled
    And there should be no module level errors

  Scenario: Invalid boolean values should raise an error
    Given I added a config file to "./category/module" with content:
      enabled = False
    When I run the dotmodules system
    Then there should be no modules loaded
    And a global error should have been raised:
      Only all lowercase booleans allowed