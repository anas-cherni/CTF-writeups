def getIndex(title : str):
    for ind, role in enumerate(DEFAULT_ROLES):
        if role['title'].upper() == title.upper():
            return ind+1
    return -1


DEFAULT_ROLES = [
    {
        "title": "Administrator"
    },
    {
        "title": "User"
    }
]

ADMIN_ROLE_ID   = getIndex("Administrator")
USER_ROLE_ID    = getIndex("User")