def enrich_metadata(text):
    lower = text.lower()

    if "must" in lower or "shall" in lower:
        obligation = "Strong"
    elif "should" in lower:
        obligation = "Medium"
    else:
        obligation = "Weak"

    if "encrypt" in lower or "security" in lower:
        control = "Security"
    elif "audit" in lower:
        control = "Audit"
    elif "privacy" in lower or "data protection" in lower:
        control = "Privacy"
    elif "risk" in lower:
        control = "Risk"
    else:
        control = "General"

    return obligation, control