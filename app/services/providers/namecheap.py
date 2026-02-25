# app/services/providers/namecheap.py

def provider_instructions(email: str):
    """
    Manual provisioning instructions
    """
    return {
        "provider": "Namecheap Private Email",
        "mode": "manual",
        "steps": [
            "Login to Namecheap",
            "Go to Private Email",
            f"Create mailbox: {email}",
            "Ensure DKIM is enabled"
        ]
    }