import smtplib
import os
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from pydantic import BaseModel, Field

class EmailToolInput(BaseModel):
    subject: str = Field(..., description="The subject of the email")
    body: str = Field(..., description="The body of the email (plain text)")
    smtp_server: Optional[str] = Field(default="smtp.gmail.com", description="SMTP server address (default: Gmail)")
    smtp_port: Optional[int] = Field(default=587, description="SMTP server port (default: 587 for TLS)")
    sender_email: Optional[str] = Field(default=None, description="Sender's email address (uses SENDER_EMAIL env var if not provided)")
    sender_password: Optional[str] = Field(default=None, description="Sender's email password (uses SENDER_PASSWORD env var if not provided)")
    
class EmailToolOutput(BaseModel):
    success: bool = Field(..., description="Indicates whether the email was sent successfully")
    message: str = Field(..., description="Result message of the email sending operation")

def send_email_tool(input_data: EmailToolInput, to_emails: List[str]) -> EmailToolOutput:
    """
    Sends an email with the specified subject and body to the given recipients.
    Uses environment variables for sender credentials if not provided in input.
    
    Environment variables:
    - SENDER_EMAIL: Default sender email address
    - SENDER_PASSWORD: Default sender app password
    """
    try:
        # Get sender credentials from input or environment variables
        sender_email = input_data.sender_email or os.getenv("SENDER_EMAIL")
        sender_password = input_data.sender_password or os.getenv("SENDER_PASSWORD")
        smtp_server = input_data.smtp_server or "smtp.gmail.com"
        smtp_port = input_data.smtp_port or 587
        
        # Validate required fields
        if not sender_email:
            return EmailToolOutput(
                success=False, 
                message="Sender email not provided. Set SENDER_EMAIL environment variable or provide sender_email in input."
            )
        if not sender_password:
            return EmailToolOutput(
                success=False, 
                message="Sender password not provided. Set SENDER_PASSWORD environment variable or provide sender_password in input."
            )
        
        # Create email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = ", ".join(to_emails)
        message["Subject"] = input_data.subject
        message.attach(MIMEText(input_data.body, "plain"))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(
                sender_email,
                to_emails,
                message.as_string()
            )

        return EmailToolOutput(success=True, message=f"Email sent to {', '.join(to_emails)}")
    except Exception as e:
        return EmailToolOutput(success=False, message=f"Failed to send email: {str(e)}")
    
def create_send_email_tool(to_emails: List[str]):
    """
    Create a send email tool function with pre-configured recipient emails.
    
    Args:
        to_emails: List of recipient email addresses (default: None)
        
    Returns:
        A function that sends emails with the specified recipients
    """
    def configured_send_email_tool(input_data: EmailToolInput) -> EmailToolOutput:
        return send_email_tool(input_data, to_emails=to_emails)
    
    return configured_send_email_tool