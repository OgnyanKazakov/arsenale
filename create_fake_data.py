import json
from faker import Faker

fake = Faker()

# Generate fake PII data
pii_data = []
for _ in range(100):  # Generate 100 records
    record = {
        "user_id": fake.uuid4(),
        "name": fake.name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "address": fake.address(),
        "ssn": fake.ssn(),
        "date_of_birth": fake.date_of_birth().isoformat(),
        "credit_card": fake.credit_card_number(),
        "job_title": fake.job(),
        "company": fake.company()
    }
    pii_data.append(record)

# Save to JSON file
with open('fake_pii_data.json', 'w') as f:
    json.dump(pii_data, f, indent=2)

print("Generated fake_pii_data.json with 100 records")
