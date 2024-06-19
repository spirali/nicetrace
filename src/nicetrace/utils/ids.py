import uuid


def generate_uid() -> str:
    return uuid.uuid4().hex
