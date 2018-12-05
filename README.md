# Bash Script Dependency Checker

A proof-of-concept static dependency checker for [ROS](http://www.ros.org) packages.
Checks for undeclared runtime dependendencies in the shell scripts found in a package.

The code can in theory also be used to check non-ROS shell scripts with modifications.

---

## Run

- Install `bashlex` and `untangle` before running `checker.py`.
- Run `checker.py` with a path to a ROS package source contain its `package.xml` file.

### Example

```bash
./checker.py my_cool_package_source
```

or

```
python3 checker.py my_cool_package_source
```

---

## Notes on ROS

This checker can in theory check any given folder with shell scripts. Certain assumptions about folder structure have been made since this has been developed with ROS in mind.

- The OS running the shell script has the available commands found on a base ROS distro (see [ROS on Docker Hub](https://hub.docker.com/_/ros/))
- A `package.xml` file is found in the (sub)folder(s) the script is run on containing a `<run_depend>` or `<exec_depend>` with the commands that are installed

In order to run on any shell script, the code needs to be modified to provide a new set of base commands and use a different type of requirement specifying file (instead of `package.xml`).
