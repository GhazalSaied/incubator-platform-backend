def user_has_role(user, role_code: str) -> bool:
    return user.userrole_set.filter(
        role__code=role_code,
        is_active=True
    ).exists()


def user_has_any_role(user, role_codes: list[str]) -> bool:
    return user.userrole_set.filter(
        role__code__in=role_codes,
        is_active=True
    ).exists()