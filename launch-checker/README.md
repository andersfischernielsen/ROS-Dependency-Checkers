# `.launch` Dependency Checker

This checker validates imported dependencies in ROS `.launch` files using the built-in ROS tools (`catkin`, `rospack`) and checks if any `$(find)`s in the `.launch` markup are undeclared in `package.xml`.

## Run

- Install dependencies using `pip/pip3 install -r requirements.txt`
- Run `checker.py` with a path to a valid ROS package containing a `package.xml`.

Example:

```bash
./checker.py Examples/FULL/universal_robot/ur5_moveit_config/
```
