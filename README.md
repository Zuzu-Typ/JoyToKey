# JoyToKey - Map your Xbox controller to keyboard keys
With JoyToKey you can create custom mappings of Xbox keys with ease.

**Windows only**

## Setup
You need to install XInput-Python and winput to use JoyToKey:
```
pip install -r requirements.txt
```

## Create a mapping
Run `configure.py` to create a new mapping.

It will allow you to create a new mapping by first pressing a **button**, pressing a **trigger** or moving a **stick** on your Xbox controller, followed by a corresponding keyboard key.

Currently mouse movement and mouse buttons cannot be used.

## Run a mapping
When you've created a mapping that you want to use, simply run:
```
python joytokey.py "<your mapping name>.j2k"
```

Sample output:
```
Mapping started with config:
A is mapped to VK_E
B is mapped to VK_Q
LEFT_STICK UP is mapped to VK_W
LEFT_STICK DOWN is mapped to VK_S
LEFT_STICK LEFT is mapped to VK_A
LEFT_STICK RIGHT is mapped to VK_D

Press CTRL + C to stop.
```

If you overwrite the mapping called "default", you can omit the mapping file parameter:
```
python joytokey.py
```
