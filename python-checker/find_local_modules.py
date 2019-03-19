import pkgutil
import sys

search_path = [sys.argv[1]]
all_modules = [x[1] for x in pkgutil.iter_modules(path=search_path)]
for m in all_modules:
    print(m)
