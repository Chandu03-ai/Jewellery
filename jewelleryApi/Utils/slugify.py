import re
def slugify(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^\w\s-]", "", name)
    return re.sub(r"[-\s]+", "-", name)
