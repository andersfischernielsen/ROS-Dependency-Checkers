# ROS Dependency Checker

A proof-of-concept static dependency checker for [ROS](http://www.ros.org) packages.

Checks for undeclared runtime dependendencies in the shell scripts found in a package. 

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
