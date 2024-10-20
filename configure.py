from j2klib import JoyToKeyConfig, JoyToKeyCreator, JoyMapper

import os

j2kc = JoyToKeyCreator()

print("Welcome to the JoyToKey configurator.")

mappings = []

while True:
    add_new_key = input("Would you like to add a new key? ([Y]/N): ")
    add_new_key = add_new_key or "Y"

    if add_new_key.upper() not in ("Y", "N"):
        print("Invalid input. Please enter Y for yes or N for no.")
        continue

    if add_new_key.upper() == "N":
        break

    print("Please press the key on your Xbox controller now.", end="\r")

    xkey = j2kc.listen_for_xinput()

    print("Now press the key on your keyboard you want to map it to.", end="\r")

    wkey = j2kc.listen_for_winput()

    xkey["key"] = wkey

    mapping = JoyMapper.from_dict(xkey)

    mappings.append(mapping)

    print(" " * 60, end="\r")

    print(mapping.explain())
    print()

cfg = JoyToKeyConfig(mappings)

print("Please name your new mapping.")
print()
mapping_name = input("name: ")

file_name = f"{mapping_name}.j2k"

cfg.to_file(file_name)

print(f"Mapping saved as {file_name}")

os.system("pause")
