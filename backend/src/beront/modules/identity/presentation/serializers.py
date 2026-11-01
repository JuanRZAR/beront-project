from beront.modules.identity.domain.policies import PERMISSIONS


def administrator_data(admin):
    return {
        "id": str(admin.id),
        "username": admin.username,
        "role": "admin",
        "permissions": sorted(PERMISSIONS),
    }
