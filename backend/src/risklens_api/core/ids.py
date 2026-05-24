import uuid


def generate_id() -> str:
    """Generate a sortable submission ID. Swap to ULID later."""
    return uuid.uuid4().hex.upper()
