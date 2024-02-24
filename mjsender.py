import smtplib
import time
import logging
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from termcolor import colored

logging.basicConfig(level=logging.INFO)

def send_email(sender_email, sender_password, recipient, subject, body, attachment_file, smtp_server, smtp_port):
    try:
        # Create a multipart message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient
        message['Subject'] = subject

        # Add body to email
        message.attach(MIMEText(body, 'plain'))

        # Open the file in binary mode
        with open(attachment_file, 'rb') as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {attachment_file}',
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        # Login to the SMTP server and send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, text)
        
        logging.info(colored(f"Email sent to {recipient}", "green"))
    except Exception as e:
        logging.error(colored(f"Error sending email to {recipient}: {str(e)}", "red"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send emails to multiple recipients with attachments.')
    parser.add_argument('-se', '--sender_email', type=str, help='Sender\'s email address.')
    parser.add_argument('-sp', '--sender_password', type=str, help='Sender\'s email password.')
    parser.add_argument('-rf', '--recipient_file', type=str, help='File containing list of recipient email addresses.')
    parser.add_argument('-sb', '--subject', type=str, help='Email subject.')
    parser.add_argument('-bd', '--body', type=str, help='Email body.')
    parser.add_argument('-af', '--attachment_file', type=str, help='Attachment file.')
    parser.add_argument('-ss', '--smtp_server', type=str, default='smtp.gmail.com', help='SMTP server address.')
    parser.add_argument('-pt', '--smtp_port', type=int, default=587, help='SMTP server port number.')
    parser.add_argument('-d', '--delay', type=int, default=10, help='Delay between sending each email (in seconds).')
    parser.add_argument('-o', '--output_file', type=str, help='Output file for logging the results.')

    args = parser.parse_args()

    # Setup logging to both console and file
    if args.output_file:
        logging.basicConfig(filename=args.output_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO)

    # Read sender's email and password from command-line arguments
    sender_email = args.sender_email
    sender_password = args.sender_password

    # Read recipient emails from file
    with open(args.recipient_file, 'r') as file:
        recipients = file.readlines()

    # Strip newlines from recipient emails
    recipients = [recipient.strip() for recipient in recipients]

    # Send emails with the specified configuration
    for recipient in recipients:
        send_email(sender_email, sender_password, recipient, args.subject, args.body, args.attachment_file, args.smtp_server, args.smtp_port)
        time.sleep(args.delay)  # Delay in seconds
