# Slack Integration Database

## Overview

This module provides a lightweight SQLite-based database solution for managing case information in the Slack integration.

## Features

- Create and track cases
- Add documents to cases
- Schedule hearings
- Retrieve case details with associated documents and hearings

## Database Schema

- **Cases Table**: Stores basic case information
  - `id`: Unique identifier
  - `case_number`: Formatted case number (YYYY-NNN)
  - `description`: Case description
  - `status`: Current case status
  - `created_at`: Timestamp of case creation
  - `channel_id`: Associated Slack channel

- **Documents Table**: Tracks documents associated with cases
  - `id`: Unique document identifier
  - `case_id`: Reference to the associated case
  - `filename`: Name of the uploaded file
  - `filetype`: File type/extension
  - `size`: File size in bytes
  - `uploaded_at`: Timestamp of document upload

- **Hearings Table**: Manages scheduled hearings for cases
  - `id`: Unique hearing identifier
  - `case_id`: Reference to the associated case
  - `hearing_date`: Scheduled date of the hearing
  - `scheduled_at`: Timestamp of hearing scheduling

## Usage Example

```python
from src.integrations.slack.database import SlackDatabase

# Initialize database
db = SlackDatabase()

# Create a new case
case = db.create_case("Breach of contract lawsuit")

# Add a document to the case
document = db.add_document(
    case_id=case['id'], 
    filename="contract.pdf", 
    filetype="pdf", 
    size=2048
)

# Schedule a hearing
hearing = db.schedule_hearing(
    case_id=case['id'], 
    hearing_date="2025-03-15"
)

# Retrieve case details
case_details = db.get_case(case['id'])
print(case_details)
```

## Testing

Run tests using pytest:

```bash
pytest tests/integrations/slack/test_slack_database.py
```

## Dependencies

- sqlite3
- uuid
- pytest (for testing)

## Limitations

- Designed for lightweight, file-based storage
- Not suitable for high-concurrency environments
- Limited to local file storage

## Future Improvements

- Add indexing for performance
- Implement more advanced querying
- Add support for case status updates
- Implement soft delete functionality
