ADMIN = "Admin"
DOCTOR = "Doctor"
RECEPTION = "Reception"

ALL_ROLES = [ADMIN, DOCTOR, RECEPTION]


def user_roles(user):
    if not user.is_authenticated:
        return []
    roles = set(user.groups.values_list("name", flat=True))
    if user.is_superuser or user.is_staff:
        roles.add(ADMIN)
    return sorted(roles)


def has_any_role(user, allowed_roles):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return bool(set(user_roles(user)) & set(allowed_roles))
