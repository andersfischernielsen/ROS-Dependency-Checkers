# `.launch` Dependency Checker

This checker validates that all `$(find <package-name>)` substitutions in all ROS `.launch` files of a package are declared in `package.xml`.

## Run

- Install dependencies using `pip3 install -r requirements.txt`
- Run `checker.py` with a path to a valid ROS package containing a `package.xml`.

Example:

```bash
./checker.py Examples/FULL/universal_robot/ur5_moveit_config/
```
