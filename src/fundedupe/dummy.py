def function_1(a: int, b: int) -> int:
    return a + b


def function_2(c: int, d: int) -> int:
    return c + d


def say_hello() -> None:
    print("Hello, there")


def combined() -> int:
    say_hello()
    return function_1(1, 2)


def one_more_function_here():
    return None


def more_complex() -> list[int]:
    output = []
    another_thing = {}
    for x in range(10):
        output.append(x)
        another_thing[x] = f"{x=}"
    print(another_thing)
    a = 1 + 2
    b = 123 + a
    a *= b
    return output


class ThisClass:
    def __init__(self, uno: float, dos: float):
        self.uno = uno
        self.dos = dos

    def product(self):
        return self.uno * self.dos
