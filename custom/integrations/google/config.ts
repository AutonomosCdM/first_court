import { z } from 'zod';

export const GoogleScopes = {
  CALENDAR: ['https://www.googleapis.com/auth/calendar'],
  FORMS: ['https://www.googleapis.com/auth/forms'],
  SHEETS: ['https://www.googleapis.com/auth/spreadsheets'],
  DRIVE: ['https://www.googleapis.com/auth/drive'],
  GMAIL: ['https://www.googleapis.com/auth/gmail.send'],
  MEET: ['https://www.googleapis.com/auth/meetings'],
};

export const Paths = {
  CREDENTIALS: '/credentials.json',
  TOKEN: '/token.pickle',
};

export const DocumentTypes = {
  CASE_INTAKE: 'case_intake',
  SATISFACTION_SURVEY: 'satisfaction_survey',
  HEARING_REPORT: 'hearing_report',
  COURT_ORDER: 'court_order',
};

export const configSchema = z.object({
  GOOGLE_APPLICATION_CREDENTIALS: z.string(),
  GOOGLE_CALENDAR_ID: z.string().optional(),
  GOOGLE_DRIVE_FOLDER: z.string().optional(),
});
