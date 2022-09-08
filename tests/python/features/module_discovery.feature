Feature: Module discovery

  As a user of the dotmodules system,
  I want to keep my individual configurations isolated,
  So that my whole configuration will be decoupled and organized.

  Dotmodules should automatically find my configuration modules based on the
  dotmodules configuration files.

  Background:
    Given I have the main modules directory at "./modules"
    And I set the dotmodules config file name as "dm.toml"

  Scenario: No modules should be tolerated
    When I run the dotmodules system
    Then there should be no modules loaded
    And there should be no module level errors

  Scenario: A configuration file cannot be placed in the main modules directory
    Given I added an empty config file to "."
    When I run the dotmodules system
    Then a global error should have been raised:
      You cannot have a config file directly in the main modules directory!

  Scenario: Modules should be able to loaded from subdirectories
    Given I added an empty config file to "./module_1"
    And I added an empty config file to "./module_2"
    When I run the dotmodules system
    Then there should be "2" loaded modules
    And the modules should have the following relative roots:
      ./modules/module_1
      ./modules/module_2
    And there should be no module level errors

  Scenario: Modules should be able to loaded from nested subdirectories
    Given I added an empty config file to "./category_1/module_1_1"
    And I added an empty config file to "./category_1/module_1_2"
    And I added an empty config file to "./category_2/module_2_1"
    When I run the dotmodules system
    Then there should be "3" loaded modules
    And the modules should have the following relative roots:
      ./modules/category_1/module_1_1
      ./modules/category_1/module_1_2
      ./modules/category_2/module_2_1
    And there should be no module level errors

  Scenario: Loaded modules should be ordered by path
    Given I added an empty config file to "./category_3/module_3"
    And I added an empty config file to "./category_1/module_1"
    And I added an empty config file to "./category_2/module_2"
    When I run the dotmodules system
    Then there should be "3" loaded modules
    And the modules should have the following relative roots in order:
      ./modules/category_1/module_1
      ./modules/category_2/module_2
      ./modules/category_3/module_3
    And there should be no module level errors