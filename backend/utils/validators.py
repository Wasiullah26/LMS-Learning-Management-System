import re


def validate_email(email):
    # check if email format is correct
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    # check password strength
    # needs at least 8 chars, one uppercase, one lowercase, one number
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
    # check if role is valid
    return role in ["student", "instructor"]


def validate_required_fields(data, required_fields):
    # check if all required fields are present
    missing = [field for field in required_fields if field not in data or data[field] is None]
    return len(missing) == 0, missing


def sanitize_string(value, max_length=None):
    # clean up string input
    if not isinstance(value, str):
        return None

    # remove extra spaces
    value = value.strip()

    # check length
    if max_length and len(value) > max_length:
        return None

    # return None if empty
    if len(value) == 0:
        return None

    return value


def validate_file_extension(filename, allowed_extensions):
    # check if file extension is allowed
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in allowed_extensions


def validate_file_size(file_size, max_size):
    # check if file size is within limit
    return file_size <= max_size
