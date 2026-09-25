import csv
import random
from pathlib import Path

random.seed(42)

TEMPLATES = {
    "billing": [
        "I was charged twice for my subscription",
        "My payment failed but money was deducted",
        "I need a refund for my recent purchase",
        "Why was I charged an extra amount on my invoice?",
        "My billing amount is incorrect",
        "I was charged for a subscription I cancelled",
        "The invoice shows the wrong amount",
        "My card was charged twice this month",
        "I want to understand this unexpected charge",
        "The refund has not reached my account yet",
    ],
    "technical": [
        "The application keeps crashing when I open it",
        "The website is showing an error",
        "I cannot upload my document",
        "The dashboard is loading very slowly",
        "The application stopped working after the update",
        "I am getting an error when trying to download a file",
        "The page keeps freezing",
        "The search feature is not working",
        "I cannot complete the requested action because of an error",
        "The system is giving me a server error",
    ],
    "account": [
        "I cannot log into my account",
        "I forgot my password and need to reset it",
        "My account is locked",
        "I am not receiving the login verification code",
        "I need to change my email address",
        "How can I update my account details?",
        "My account access stopped working",
        "I cannot verify my identity",
        "I want to change the phone number linked to my account",
        "My login credentials are not being accepted",
    ],
    "feature_request": [
        "Please add dark mode to the application",
        "It would be useful to have a mobile application",
        "Can you add an option to export reports?",
        "I would like a custom notification feature",
        "Please add support for more languages",
        "It would be helpful to have bulk upload",
        "Can you add filtering to the dashboard?",
        "I would like an integration with Google Drive",
        "Please add a calendar view",
        "Can you provide an API for this feature?",
    ],
}

MODIFIERS = [
    "Please help me with this.",
    "This is causing a problem for me.",
    "I need this resolved as soon as possible.",
    "Could you please look into this?",
    "This has been happening since yesterday.",
    "I have already tried several times.",
    "Please let me know what I should do.",
    "This is quite frustrating.",
    "I would appreciate a quick response.",
    "Can someone help me resolve this?",
]

ROWS = []

for category, templates in TEMPLATES.items():
    for _ in range(40):
        template = random.choice(templates)
        modifier = random.choice(MODIFIERS)

        ROWS.append(
            {
                "text": f"{template}. {modifier}",
                "category": category,
            }
        )

random.shuffle(ROWS)

output_path = Path(__file__).parent / "tickets.csv"

with output_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["text", "category"])
    writer.writeheader()
    writer.writerows(ROWS)

print(f"Created {len(ROWS)} tickets")
print(f"Saved to: {output_path}")
