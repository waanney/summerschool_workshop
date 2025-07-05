import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

def send_email_tool(subject: str, body: str, to_emails: List[str], smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
    """
    Sends an email with the specified subject and body to the given recipients.
    
    Parameters:
    - subject (str): The subject of the email.
    - body (str): The body of the email (plain text).
    - to_emails (List[str]): List of recipient email addresses.
    - smtp_server (str): SMTP server address (e.g., 'smtp.gmail.com').
    - smtp_port (int): SMTP server port (usually 587 for TLS).
    - sender_email (str): Sender's email address.
    - sender_password (str): Sender's email password (use app-specific passwords for services like Gmail).
    """
    # Create the email header
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(to_emails)
    message["Subject"] = subject

    # Attach the body of the email to the MIME message
    message.attach(MIMEText(body, "plain"))

    # Connect to the SMTP server
    try:
        # Set up the SMTP server (Gmail in this example)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)  # Log in using sender's email and password
            server.sendmail(sender_email, to_emails, message.as_string())  # Send the email
            print(f"Email sent successfully to {', '.join(to_emails)}")

    except Exception as e:
        print(f"Failed to send email: {str(e)}")

