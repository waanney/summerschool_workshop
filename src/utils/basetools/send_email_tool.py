"""
Email sending and configuration module.

This module provides functionality for sending emails using SMTP with support
for Gmail and other email providers. It handles authentication, message formatting,
and error handling with configurable sender and recipient settings.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Callable
from enum import Enum

from pydantic import BaseModel, Field


class EmailProvider(str, Enum):
    """Enum for supported email providers."""

    GMAIL = "gmail"
    OUTLOOK = "outlook"
    YAHOO = "yahoo"
    CUSTOM = "custom"


class EmailStatus(str, Enum):
    """Enum for email sending status."""

    SUCCESS = "success"
    FAILED = "failed"
    INVALID_CREDENTIALS = "invalid_credentials"
    INVALID_RECIPIENTS = "invalid_recipients"
    SMTP_ERROR = "smtp_error"


class EmailToolInput(BaseModel):
    """Input model for email sending operations."""

    subject: str = Field(..., description="The subject of the email")
    body: str = Field(..., description="The body of the email (plain text)")
    html_body: Optional[str] = Field(None, description="HTML version of the email body")


class EmailToolOutput(BaseModel):
    """Output model for email sending operations."""

    success: bool = Field(
        ..., description="Indicates whether the email was sent successfully"
    )
    message: str = Field(
        ..., description="Result message of the email sending operation"
    )
    status: EmailStatus = Field(
        EmailStatus.FAILED, description="Status of the email operation"
    )


def send_email_tool(
    input_data: EmailToolInput,
    to_emails: List[str],
    sender_email: Optional[str] = None,
    sender_password: Optional[str] = None,
    provider: EmailProvider = EmailProvider.GMAIL,
) -> EmailToolOutput:
    """
    Send an email with the specified subject and body to the given recipients.

    This function sends emails using SMTP with support for multiple email providers.
    It uses environment variables for sender credentials if not provided in input.
    Supports both plain text and HTML email bodies.

    Args:
        input_data: EmailToolInput object containing email content
        to_emails: List of recipient email addresses
        sender_email: Sender email address (uses SENDER_EMAIL env var if not provided)
        sender_password: Sender password/app password (uses SENDER_PASSWORD env var if not provided)
        provider: Email provider to use for SMTP configuration

    Returns:
        EmailToolOutput: Object containing email sending results and metadata

    Raises:
        smtplib.SMTPAuthenticationError: If authentication fails
        smtplib.SMTPRecipientsRefused: If recipients are invalid
        smtplib.SMTPServerDisconnected: If SMTP server connection fails
        Exception: For any other email sending errors

    Environment variables:
        SENDER_EMAIL: Default sender email address
        SENDER_PASSWORD: Default sender app password
    """
    try:
        # Get sender credentials from input or environment variables
        sender_email = sender_email or os.getenv("SENDER_EMAIL")
        sender_password = sender_password or os.getenv("SENDER_PASSWORD")

        # Get SMTP configuration based on provider
        smtp_config: tuple[str, int] = _get_smtp_config(provider)
        smtp_server: str = smtp_config[0]
        smtp_port: int = smtp_config[1]

        # Validate required fields
        if not sender_email:
            return EmailToolOutput(
                success=False,
                message="Sender email not provided. Set SENDER_EMAIL environment variable or provide sender_email in input.",
                status=EmailStatus.INVALID_CREDENTIALS,
            )
        if not sender_password:
            return EmailToolOutput(
                success=False,
                message="Sender password not provided. Set SENDER_PASSWORD environment variable or provide sender_password in input.",
                status=EmailStatus.INVALID_CREDENTIALS,
            )
        if not to_emails:
            return EmailToolOutput(
                success=False,
                message="No recipient emails provided.",
                status=EmailStatus.INVALID_RECIPIENTS,
            )

        # Create email message
        message: MIMEMultipart = _create_email_message(
            sender_email, to_emails, input_data
        )

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_emails, message.as_string())

        return EmailToolOutput(
            success=True,
            message=f"Email sent to {', '.join(to_emails)}",
            status=EmailStatus.SUCCESS,
        )

    except smtplib.SMTPAuthenticationError:
        return EmailToolOutput(
            success=False,
            message="Authentication failed. Check sender email and password.",
            status=EmailStatus.INVALID_CREDENTIALS,
        )
    except smtplib.SMTPRecipientsRefused:
        return EmailToolOutput(
            success=False,
            message="Invalid recipient email addresses.",
            status=EmailStatus.INVALID_RECIPIENTS,
        )
    except smtplib.SMTPServerDisconnected:
        return EmailToolOutput(
            success=False,
            message="SMTP server connection failed.",
            status=EmailStatus.SMTP_ERROR,
        )
    except Exception as e:
        return EmailToolOutput(
            success=False,
            message=f"Failed to send email: {str(e)}",
            status=EmailStatus.FAILED,
        )


def _get_smtp_config(provider: EmailProvider) -> tuple[str, int]:
    """
    Get SMTP server configuration for the specified email provider.

    Args:
        provider: Email provider to get configuration for

    Returns:
        tuple[str, int]: SMTP server and port configuration
    """
    if provider == EmailProvider.GMAIL:
        return "smtp.gmail.com", 587
    elif provider == EmailProvider.OUTLOOK:
        return "smtp-mail.outlook.com", 587
    elif provider == EmailProvider.YAHOO:
        return "smtp.mail.yahoo.com", 587
    else:
        return "smtp.gmail.com", 587  # Default fallback


def _create_email_message(
    sender_email: str, to_emails: List[str], input_data: EmailToolInput
) -> MIMEMultipart:
    """
    Create a MIME email message with the specified content.

    Args:
        sender_email: Sender email address
        to_emails: List of recipient email addresses
        input_data: Email content and configuration

    Returns:
        MIMEMultipart: Configured email message object
    """
    message: MIMEMultipart = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = ", ".join(to_emails)
    message["Subject"] = input_data.subject

    # Add plain text body
    text_part: MIMEText = MIMEText(input_data.body, "plain")
    message.attach(text_part)

    # Add HTML body if provided
    if input_data.html_body:
        html_part: MIMEText = MIMEText(input_data.html_body, "html")
        message.attach(html_part)

    return message


def create_send_email_tool(
    to_emails: List[str],
    sender_email: Optional[str] = None,
    sender_password: Optional[str] = None,
    provider: EmailProvider = EmailProvider.GMAIL,
) -> Callable[[EmailToolInput], EmailToolOutput]:
    """
    Create a send email tool function with pre-configured settings.

    This factory function creates a configured email sending function that uses
    specific recipient emails, sender credentials, and email provider. These
    settings are fixed and cannot be changed by the calling code.

    Args:
        to_emails: List of recipient email addresses
        sender_email: Sender email address (optional, uses env var if not provided)
        sender_password: Sender password (optional, uses env var if not provided)
        provider: Email provider to use

    Returns:
        Callable[[EmailToolInput], EmailToolOutput]: A function that sends emails with the specified configuration

    Example:
        >>> email_tool = create_send_email_tool(["user@example.com"])
        >>> result = email_tool(EmailToolInput(subject="Test", body="Hello"))
    """

    def configured_send_email_tool(input_data: EmailToolInput) -> EmailToolOutput:
        """
        Configured email sending function with fixed settings.

        Args:
            input_data: EmailToolInput object containing email content

        Returns:
            EmailToolOutput: Object containing email sending results and metadata
        """
        return send_email_tool(
            input_data,
            to_emails=to_emails,
            sender_email=sender_email,
            sender_password=sender_password,
            provider=provider,
        )

    return configured_send_email_tool
