from tail_recursion import tail_recursive, recurse

@tail_recursive
def factorial(n, prod=1):
    if n == 0:
        return prod
    else:
        return recurse(
            n - 1,
            n * prod
        )

@tail_recursive
def fibonacci(n, a=1, b=1):
    if n == 0:
        return a
    elif n==1:
        return b
    else:
        return recurse(
            n - 1,
            b,
            a + b
        )

@tail_recursive
def gcd(a, b):
    if a > b:
        a, b = b, a
    if a == 0:
        return b
    else:
        return recurse(
            b - a,
            a
        )

print(factorial(500))
print(fibonacci(500))
print(gcd(128, 320))
