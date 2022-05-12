def deco(func):
    def ans(*args):
        func(*args)
    return ans


@deco
def mul_test(x, y):
    print((x*y))


mul_test(23, 3)
