# Python Dependency Checker

This checker validates imported dependencies using `flake8` with the `flake8-requirements` plugin as a base checker with a bit of ROS-specific code on top. 

The checker generates a Python `requirements.txt` file using the built-in ROS tools and checks if any modules used in the Python scripts of the project are undeclared in `package.xml`. 


## Run

- Install `flake8` and `flake8-requirements`
  - `python3 -m pip install flake8 flake8-requirements`
  - If on macOS, `brew install ggrep` as well
- Run `checker.sh` with a path to a valid ROS package containing a `package.xml`

Example: 

```bash
./checker.sh Examples/FULL/cob_command_gui
```
