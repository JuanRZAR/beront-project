import logging
import smtplib
import ssl
from concurrent.futures import ThreadPoolExecutor
from email.message import EmailMessage

TIMEOUT_SECONDS = 10


class SmtpMailer:
    def __init__(self, settings):
        self.settings = settings

    @property
    def configured(self):
        return bool(self.settings.smtp_host)

    def send(self, recipient, subject, body):
        settings = self.settings
        message = EmailMessage()
        message["From"], message["To"], message["Subject"] = (
            settings.smtp_sender,
            recipient,
            subject,
        )
        message.set_content(body)
        if settings.smtp_security == "ssl":
            client = smtplib.SMTP_SSL(
                settings.smtp_host,
                settings.smtp_port,
                timeout=TIMEOUT_SECONDS,
                context=ssl.create_default_context(),
            )
        else:
            client = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=TIMEOUT_SECONDS)
        with client:
            if settings.smtp_security == "starttls":
                client.starttls(context=ssl.create_default_context())
            if settings.smtp_username:
                client.login(settings.smtp_username, settings.smtp_password)
            client.send_message(message)


class BackgroundMailer:
    """Sends outside the request so response time does not reveal whether an order matched."""

    def __init__(self, mailer):
        self.mailer = mailer
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="beront-mail")

    @property
    def configured(self):
        return self.mailer.configured

    def send(self, recipient, subject, body):
        self.executor.submit(self._deliver, recipient, subject, body)

    def _deliver(self, recipient, subject, body):
        try:
            self.mailer.send(recipient, subject, body)
        except Exception as error:
            logging.getLogger("beront").error(
                "orders.recovery_mail_failed", extra={"exception_type": type(error).__name__}
            )
