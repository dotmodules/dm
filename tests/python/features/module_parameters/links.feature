Feature: Module links

  As a user of the dotmodules system,
  I want create symbolic links for files located in the module directories,
  So that I can add configuration or scripts into external places,
  While keeping the all configuration files isolated.

  Background:
    Given I have the main modules directory at "./modules"
    And I set the dotmodules config file name as "dm.toml"

  Scenario: Link definitions are not mandatory
    Given I added an empty config file to "./module_1"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have "0" links registered
    And there should be no module level errors

  Scenario: Marking existing files from my module directory as link targets
    Given I added a config file to "./category/module" with content:
      [[link]]
      name = "My link"
      path_to_target = "./bin/my_script.sh"
      path_to_symlink = "my/path/to/symlink"
    And I added an empty file to "./category/module/bin/my_script.sh"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have "1" link registered
    And there should be no module level errors

  Scenario: Marking existing directories from my module directory as link targets
    Given I added a config file to "./category/module" with content:
      [[link]]
      name = "My link"
      path_to_target = "./config"
      path_to_symlink = "my/path/to/symlink"
    And I added a directory to "./category/module/config"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have "1" link registered
    And there should be no module level errors

  Scenario: Path to targets should exist
    Given I added a config file to "./category/module" with content:
      [[link]]
      name = "My link"
      path_to_target = "my/path/to/target"
      path_to_symlink = "my/path/to/symlink"
    When I run the dotmodules system
    Then there should be "1" loaded module
    And the module at index "1" should have "1" link registered
    And there should be a module level error for module at index "1":
      Link[My link]: path_to_target 'my/path/to/target' does not name a file or directory!