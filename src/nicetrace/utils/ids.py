import random
import string

chars = string.ascii_letters + string.digits


def generate_uid() -> str:
    return "".join(random.choice(chars) for _ in range(10))
