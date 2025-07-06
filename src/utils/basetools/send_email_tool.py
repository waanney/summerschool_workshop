import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from pydantic import BaseModel, Field

class EmailToolInput(BaseModel):
    subject: str = Field(..., description="The subject of the email")
    body: str = Field(..., description="The body of the email (plain text)")
    to_emails: List[str] = Field(..., description="List of recipient email addresses")
    smtp_server: str = Field(..., description="SMTP server address (e.g., 'smtp.gmail.com')")
    smtp_port: int = Field(..., description="SMTP server port (usually 587 for TLS)")
    sender_email: str = Field(..., description="Sender's email address")
    sender_password: str = Field(..., description="Sender's email password (use app-specific passwords for services like Gmail)")
    
class EmailToolOutput(BaseModel):
    success: bool = Field(..., description="Indicates whether the email was sent successfully")
    message: str = Field(..., description="Message indicating the result of the email sending operation")


def send_email_tool(input_data: EmailToolInput) -> EmailToolOutput:
    """
    Sends an email with the specified subject and body to the given recipients.
    """
    try:
        message = MIMEMultipart()
        message["From"] = input_data.sender_email
        message["To"] = ", ".join(input_data.to_emails)
        message["Subject"] = input_data.subject
        message.attach(MIMEText(input_data.body, "plain"))

        with smtplib.SMTP(input_data.smtp_server, input_data.smtp_port) as server:
            server.starttls()
            server.login(input_data.sender_email, input_data.sender_password)
            server.sendmail(
                input_data.sender_email,
                input_data.to_emails,
                message.as_string()
            )
        return EmailToolOutput(success=True, message=f"Email sent successfully to {', '.join(input_data.to_emails)}")
    except Exception as e:
        return EmailToolOutput(success=False, message=f"Failed to send email: {str(e)}")
