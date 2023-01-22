Feature: Module built in documentation

  As a user of the dotmodules system,
  I want to add documentation to my modules,
  So it could be shared with others more easily.

  Background:
    Given I have the main modules directory at "./modules"
    And I set the dotmodules config file name as "dm.toml"

  Scenario: Documentation is not mandatory
    Given I added an empty config file to "./module"
    And I am using the default deployment target
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have empty documentation
    And there should be no module level errors
    And there should be no module level warnings

  Scenario: Single line documentation is valid with single quotes
    Given I added a config file to "./module" with content:
      documentation = 'This is the documentation'
    And I am using the default deployment target
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have its documentation set to:
      This is the documentation
    And there should be no module level errors
    And there should be no module level warnings

  Scenario: Single line documentation is valid with double quotes
    Given I added a config file to "./module" with content:
      documentation = "This is the documentation"
    And I am using the default deployment target
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have its documentation set to:
      This is the documentation
    And there should be no module level errors
    And there should be no module level warnings

  Scenario: Multiline documentation indentation will be kept
    Given I added a config file to "./module" with content:
      documentation = """
      line 1
      line 2
        indented line 1
        indented line 2
      line 3
      """
    And I am using the default deployment target
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have its documentation set to:
      line 1
      line 2
        indented line 1
        indented line 2
      line 3
    And there should be no module level errors
    And there should be no module level warnings

  Scenario: Documentation is not mandatory even with a custom deployment target
    Given I added an empty config file to "./module"
    And I am using the "custom" deployment target
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have empty documentation
    And there should be no module level errors
    And there should be no module level warnings

  Scenario: Targeteted documentation will be kept only
    Given I added a config file to "./module" with content:
      documentation__target_1 = "Documentation for deployment target_1"
      documentation__target_2 = "Documentation for deployment target_2"
      documentation__target_3 = "Documentation for deployment target_3"
    And I am using the "target_2" deployment target
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have its documentation set to:
      Documentation for deployment target_2
    And there should be no module level errors
    And there should be no module level warnings
