# Utility function to get a user ID for a specific service
def get_identity(user, service):
    for identity in user.identities:
        if identity.service == service:
            return identity.id
