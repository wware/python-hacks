import os

os.system("make")


def test_this():
    os.system("gdb -x hook.x `which python`")


if __name__ == "__main__":
    import hook
    hook.my_dumb_hook()
