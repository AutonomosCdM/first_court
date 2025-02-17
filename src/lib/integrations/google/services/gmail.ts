import { google } from 'googleapis';
import { GoogleAuth } from '../auth';

export class GmailService {
  private gmail;

  constructor() {
    const auth = GoogleAuth.getInstance().getClient();
    this.gmail = google.gmail({ version: 'v1', auth });
  }

  async sendEmail(to: string, subject: string, body: string) {
    try {
      const utf8Subject = `=?utf-8?B?${Buffer.from(subject).toString('base64')}?=`;
      const messageParts = [
        'From: First Court <noreply@firstcourt.com>',
        `To: ${to}`,
        'Content-Type: text/html; charset=utf-8',
        'MIME-Version: 1.0',
        `Subject: ${utf8Subject}`,
        '',
        body,
      ];
      const message = messageParts.join('\n');
      const encodedMessage = Buffer.from(message)
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');

      await this.gmail.users.messages.send({
        userId: 'me',
        requestBody: {
          raw: encodedMessage,
        },
      });

      return true;
    } catch (error) {
      console.error('Error sending email:', error);
      throw error;
    }
  }
}
