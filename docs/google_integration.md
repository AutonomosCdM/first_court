# Google Integration Documentation

## Overview
This document describes the integration with Google services in the First Court system.

## Components

### OAuth2 Client (`src/auth/oauth_client.py`)
- Centralized authentication for all Google APIs
- Handles token persistence and refresh
- Supports multiple API services

### Google Forms Client (`src/integrations/google_forms.py`)
- Creates and manages forms for data collection
- Supports multiple question types:
  - Text input
  - Multiple choice (Radio)
  - File upload
- Pre-built templates:
  - Case intake form
  - Satisfaction survey

### Google Sheets Client (`src/integrations/google_sheets.py`)
- Creates and manages spreadsheets for data analysis
- Features:
  - Create new spreadsheets
  - Add/modify sheets
  - Read/write values
  - Generate reports and dashboards

## Authentication
- Credentials stored in `/credentials.json`
- Token persistence via `/token.pickle`
- Required scopes defined in `src/config/google_api_config.py`

## Usage Examples

### Creating a Case Intake Form
```python
forms_client = GoogleFormsClient()
form = forms_client.create_case_intake_form()
```

### Creating a Dashboard
```python
sheets_client = GoogleSheetsClient()
spreadsheet = sheets_client.create_spreadsheet("Case Dashboard")
sheets_client.add_sheet(spreadsheet["spreadsheetId"], "Monthly Stats")
```

## Testing
Test files are available for both integrations:
- `tests/test_forms_integration.py`
- `tests/test_sheets_integration.py`

Run tests with:
```bash
python -m unittest tests/test_forms_integration.py tests/test_sheets_integration.py -v
```
