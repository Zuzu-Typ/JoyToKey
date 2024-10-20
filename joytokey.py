import os
import sys

from j2klib import JoyToKeyConfig, JoyToKey


HERE = os.path.realpath(os.path.dirname(__file__))

DEFAULT_FILE_NAME = "default.j2k"

if len(sys.argv) == 1:
    file_path = os.path.join(HERE, DEFAULT_FILE_NAME)
    
elif len(sys.argv) == 2:
    file_path = sys.argv[1]

else:
    raise Exception("You can specify exactly one config file.")

cfg = JoyToKeyConfig.from_file(file_path)
j2k = JoyToKey(cfg)
print("Mapping started with config:")
print(cfg.explain())

print()

print("Press CTRL + C to stop.")
try:
    j2k.run()
except KeyboardInterrupt:
    print("Mapping stopped")
