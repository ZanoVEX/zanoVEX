def create_mailbox(domain: str, email: str):
    """
    This will later call Zoho Mail API
    """
    return {
        "provider": "zoho",
        "email": email,
        "status": "created"
    }