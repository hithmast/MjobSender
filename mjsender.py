import smtplib
import time
import random
import logging
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from termcolor import colored

def setup_logger(output_file=None):
    """Set up logging configuration."""
    logging.basicConfig(filename=output_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_recipients(file_path):
    """Read recipient emails from a file."""
    try:
        with open(file_path, 'r') as file:
            recipients = [line.strip() for line in file.readlines()]
            if not recipients:
                raise ValueError("Recipient list is empty.")
        return recipients
    except FileNotFoundError:
        logging.error(colored("Recipient file not found.", "red"))
        exit(1)
    except ValueError as ve:
        logging.error(colored(f"Error in recipient list: {str(ve)}", "red"))
        exit(1)

def send_email(sender_email, sender_password, recipient, subject, body, attachment_file, smtp_server, smtp_port):
    """Send an email to a single recipient."""
    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with open(attachment_file, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {attachment_file}')
            message.attach(part)

        text = message.as_string()

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, text)
        
        logging.info(colored(f"Email sent to {recipient}", "green"))
    except Exception as e:
        logging.error(colored(f"Error sending email to {recipient}: {str(e)}", "red"))

def send_emails(sender_email, sender_password, recipients, subject, body, attachment_file, smtp_server, smtp_port, delay_min, delay_max):
    """Send emails to multiple recipients."""
    for recipient in recipients:
        send_email(sender_email, sender_password, recipient, subject, body, attachment_file, smtp_server, smtp_port)
        random_delay = random.randint(delay_min, delay_max)
        time.sleep(random_delay)

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Send emails to multiple recipients with attachments.', add_help=False)
    parser.add_argument('-se', '--sender_email', type=str, required=True, help='Sender\'s email address.')
    parser.add_argument('-sp', '--sender_password', type=str, required=True, help='Sender\'s email password.')
    parser.add_argument('-rf', '--recipient_file', type=str, required=True, help='File containing list of recipient email addresses.')
    parser.add_argument('-sb', '--subject', type=str, required=True, help='Email subject.')
    parser.add_argument('-bd', '--body', type=str, required=True, help='Email body.')
    parser.add_argument('-af', '--attachment_file', type=str, required=True, help='Attachment file.')
    parser.add_argument('-ss', '--smtp_server', type=str, default='smtp.gmail.com', help='SMTP server address.')
    parser.add_argument('-pt', '--smtp_port', type=int, default=587, help='SMTP server port number.')
    parser.add_argument('-dmin', '--delay_min', type=int, default=60, help='Minimum delay in seconds.')
    parser.add_argument('-dmax', '--delay_max', type=int, default=180, help='Maximum delay in seconds.')
    parser.add_argument('-o', '--output_file', type=str, help='Output file for logging the results.')

    args = parser.parse_args()

    missing_args = []
    if not args.sender_email:
        missing_args.append("-se/--sender_email")
    if not args.sender_password:
        missing_args.append("-sp/--sender_password")
    if not args.recipient_file:
        missing_args.append("-rf/--recipient_file")
    if not args.subject:
        missing_args.append("-sb/--subject")
    if not args.body:
        missing_args.append("-bd/--body")
    if not args.attachment_file:
        missing_args.append("-af/--attachment_file")

    if missing_args:
        print("Error: The following arguments are required:", ", ".join(missing_args))
        exit(1)

    return args

if __name__ == "__main__":
    args = parse_arguments()
    setup_logger(args.output_file)
    recipients = read_recipients(args.recipient_file)
    send_emails(args.sender_email, args.sender_password, recipients, args.subject, args.body, args.attachment_file, args.smtp_server, args.smtp_port, args.delay_min, args.delay_max)
