
import XInput
import winput
import json

from typing import Self

__version__ = "0.1.0"

TRIGGER_THRESHOLD = 0.25

STICK_THRESHOLD = 0.5

class JoyMapper:
    @staticmethod
    def from_dict(data : dict) -> Self:
        assert "type" in data

        match data["type"]:
            case "button":
                return JoyButtonMapper.from_dict(data)
            case "trigger":
                return JoyTriggerMapper.from_dict(data)
            case "stick":
                return JoyStickMapper.from_dict(data)
            
        raise ValueError("Invalid data")

    def press(self) -> None:
        raise NotImplementedError()
    
    def release(self) -> None:
        raise NotImplementedError()
    
    def to_dict(self) -> dict:
        raise NotImplementedError()
    
    def explain(self) -> str:
        raise NotImplementedError()
    
class JoyButtonMapper(JoyMapper):

    def __init__(self, joy_button : int, winput_key : int):
        self.__button = joy_button
        self.__key = winput_key

    @classmethod
    def from_dict(cls, data : dict) -> None:
        assert "button" in data
        assert "key" in data

        assert isinstance(data["button"], int)
        assert isinstance(data["key"], int)

        return cls(data["button"], data["key"])
    
    def to_dict(self) -> dict:
        return {
            "type" : "button",
            "button" : self.__button,
            "key" : self.__key
        }

    @property
    def button(self) -> int:
        return self.__button

    def press(self):
        winput.press_key(self.__key)
    
    def release(self):
        winput.release_key(self.__key)

    def explain(self):
        return f"{XInput._button_dict[self.__button]} is mapped to {winput.all_vk_codes[self.__key]}"

class JoyTriggerMapper(JoyMapper):

    def __init__(self, trigger : int, winput_key : int):
        self.__trigger = trigger
        self.__key = winput_key
        self.__pressed = False

    @classmethod
    def from_dict(cls, data : dict) -> None:
        assert "trigger" in data
        assert "key" in data

        assert isinstance(data["trigger"], int)
        assert isinstance(data["key"], int)

        return cls(data["trigger"], data["key"])
    
    def to_dict(self) -> dict:
        return {
            "type" : "trigger",
            "trigger" : self.__trigger,
            "key" : self.__key
        }

    @property
    def trigger(self) -> int:
        return self.__trigger

    def press(self):
        if self.__pressed:
            return
        self.__pressed = True
        winput.press_key(self.__key)
    
    def release(self):
        if not self.__pressed:
            return
        self.__pressed = False
        winput.release_key(self.__key)

    def explain(self):
        name = "LEFT_TRIGGER" if self.__trigger == XInput.LEFT else "RIGHT_TRIGGER"
        return f"{name} is mapped to {winput.all_vk_codes[self.__key]}"

class JoyStickMapper(JoyMapper):

    def __init__(self, stick : int, direction : tuple[int], winput_key : int):
        self.__stick = stick
        self.__direction = direction
        self.__key = winput_key
        self.__pressed = False

    @classmethod
    def from_dict(cls, data : dict) -> None:
        assert "stick" in data
        assert "direction" in data
        assert "key" in data

        assert isinstance(data["stick"], int)
        assert isinstance(data["direction"], list)
        assert isinstance(data["key"], int)

        return cls(data["stick"], data["direction"], data["key"])
    
    def to_dict(self) -> dict:
        return {
            "type" : "stick",
            "stick" : self.__stick,
            "direction" : self.__direction,
            "key" : self.__key
        }

    @property
    def stick(self) -> int:
        return self.__stick
    
    @property
    def direction(self) -> tuple[int]:
        return self.__direction

    def press(self):
        if self.__pressed:
            return
        self.__pressed = True
        winput.press_key(self.__key)
    
    def release(self):
        if not self.__pressed:
            return
        self.__pressed = False
        winput.release_key(self.__key)

    def explain(self):
        name = "LEFT_STICK" if self.__stick == XInput.LEFT else "RIGHT_STICK"
        direction = "RIGHT" if self.__direction[0] == 1 else \
                    "LEFT"  if self.__direction[0] == -1 else \
                    "UP"    if self.__direction[1] == 1 else \
                    "DOWN"
        return f"{name} {direction} is mapped to {winput.all_vk_codes[self.__key]}"

class JoyToKeyConfig:
    
    def __init__(self, joy_mappers : list[JoyMapper]):
        self.__mappers = joy_mappers

    @property
    def button_mappers(self) -> list[JoyButtonMapper]:
        return list(filter(lambda mapper: isinstance(mapper, JoyButtonMapper), self.__mappers))

    @property
    def trigger_mappers(self) -> list[JoyTriggerMapper]:
        return list(filter(lambda mapper: isinstance(mapper, JoyTriggerMapper), self.__mappers))

    @property
    def stick_mappers(self) -> list[JoyStickMapper]:
        return list(filter(lambda mapper: isinstance(mapper, JoyStickMapper), self.__mappers))
    
    def explain(self) -> str:
        return "\n".join([mapper.explain() for mapper in self.__mappers])

    @classmethod
    def from_file(cls, filepath : str):
        with open(filepath, "r") as file:
            data = json.load(file)

            assert "version" in data
            assert "mappers" in data

            assert data["version"] <= __version__, "The specified file was created in a newer version."

            mappers = [JoyMapper.from_dict(mapper_dict) for mapper_dict in data["mappers"]]

            return cls(mappers)
        
    def to_file(self, filepath : str):
        with open(filepath, "w") as file:
            data = {
                "version" : __version__,
                "mappers" : [mapper.to_dict() for mapper in self.__mappers]
            }

            json.dump(data, file, indent=2)

class JoyToKey:
    def __init__(self, config : JoyToKeyConfig):
        self.__button_mappers = {mapper.button : mapper for mapper in config.button_mappers}
        self.__trigger_mappers = {mapper.trigger : mapper for mapper in config.trigger_mappers}
        self.__stick_mappers = {(mapper.stick, *mapper.direction) : mapper for mapper in config.stick_mappers}

        self.__config = config

    def run(self):
        while True:
            for event in XInput.get_events():
                if event.type == XInput.EVENT_BUTTON_PRESSED:
                    self.__process_button_press_event(event)

                elif event.type == XInput.EVENT_BUTTON_RELEASED:
                    self.__process_button_release_event(event)

                elif event.type == XInput.EVENT_TRIGGER_MOVED:
                    self.__process_trigger_event(event)

                elif event.type == XInput.EVENT_STICK_MOVED:
                    self.__process_stick_event(event)

    def __process_button_press_event(self, event : XInput.Event):
        if event.button_id not in self.__button_mappers:
            return
        
        self.__button_mappers[event.button_id].press()

    def __process_button_release_event(self, event : XInput.Event):
        if event.button_id not in self.__button_mappers:
            return
        
        self.__button_mappers[event.button_id].release()

    def __process_trigger_event(self, event : XInput.Event):
        if event.trigger not in self.__trigger_mappers:
            return
        
        if event.value >= TRIGGER_THRESHOLD:
            self.__trigger_mappers[event.trigger].press()
        else:
            self.__trigger_mappers[event.trigger].release()

    def __process_stick_event(self, event : XInput.Event):
        
        for stick, x, y in self.__stick_mappers:
            if stick != event.stick:
                continue

            mapper = self.__stick_mappers[(stick, x, y)]

            match (x, y):
                case (1, 0):
                    if event.x > STICK_THRESHOLD:
                        mapper.press()
                    else:
                        mapper.release()

                case (-1, 0):
                    if event.x < -STICK_THRESHOLD:
                        mapper.press()
                    else:
                        mapper.release()

                case (0, 1):
                    if event.y > STICK_THRESHOLD:
                        mapper.press()
                    else:
                        mapper.release()

                case (0, -1):
                    if event.y < -STICK_THRESHOLD:
                        mapper.press()
                    else:
                        mapper.release()

class JoyToKeyCreator:

    def __init__(self):
        pass

    def listen_for_xinput(self):
        list(XInput.get_events())
        while True:
            events = XInput.get_events()

            for event in events:
                if event.type == XInput.EVENT_BUTTON_PRESSED:
                    return {"type" : "button", "button" : event.button_id}
                elif event.type == XInput.EVENT_TRIGGER_MOVED and event.value > TRIGGER_THRESHOLD:
                    return {"type" : "trigger", "trigger" : event.trigger}
                elif event.type == XInput.EVENT_STICK_MOVED:
                    if event.x > STICK_THRESHOLD:
                        return {"type" : "stick", "stick" : event.stick, "direction" : [1, 0]}
                    elif event.x < -STICK_THRESHOLD:
                        return {"type" : "stick", "stick" : event.stick, "direction" : [-1, 0]}
                    elif event.y > STICK_THRESHOLD:
                        return {"type" : "stick", "stick" : event.stick, "direction" : [0, 1]}
                    elif event.y < -STICK_THRESHOLD:
                        return {"type" : "stick", "stick" : event.stick, "direction" : [0, -1]}

    def __winput_callback(self, event: winput.KeyboardEvent):

        self.__winput_key_result = event.key
        
        return winput.WP_DONT_PASS_INPUT_ON | winput.WP_UNHOOK | winput.WP_STOP

    def listen_for_winput(self) -> int:
        winput.hook_keyboard(self.__winput_callback)

        winput.wait_messages()

        winput.unhook_keyboard()

        return self.__winput_key_result

