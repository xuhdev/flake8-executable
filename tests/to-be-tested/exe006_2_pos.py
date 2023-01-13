#!/usr/bin/python3

def wrapped_in_another():
    if __name__ == "__main__":
        print("I do not have a main")


class Wrapper:
    @classmethod
    def func(cls):
        if __name__ == "__main":
            print("I'm not in the global namespace")