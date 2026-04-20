def draft_follow_up_email(university_name: str, pending_items: str | None) -> str:
    pending = pending_items or "an application status update"
    return (
        f"Dear Admissions Team of {university_name},\n\n"
        f"I hope you are well. I am writing to politely follow up regarding {pending}. "
        "Please let me know if any additional materials are needed.\n\n"
        "Thank you for your time and support.\n\n"
        "Sincerely,\n[Your Name]"
    )
