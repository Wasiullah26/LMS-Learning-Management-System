import re


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    return True, None


def validate_role(role):
    return role in ["student", "instructor"]


def validate_required_fields(data, required_fields):
    missing = [field for field in required_fields if field not in data or data[field] is None]
    return len(missing) == 0, missing


def sanitize_string(value, max_length=None):
    if not isinstance(value, str):
        return None

    value = value.strip()

    if max_length and len(value) > max_length:
        return None

    if len(value) == 0:
        return None

    return value


def validate_file_extension(filename, allowed_extensions):
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in allowed_extensions


def validate_file_size(file_size, max_size):
    return file_size <= max_size
