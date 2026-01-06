import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from app.db.session import get_session
from app.entities.order import Order
from app.entities.setting import Setting
from app.entities.user import User
from app.repositories.setting_repository import SettingRepository
from app.services.encrypted_type import decrypt_value


class EmailService:
    def __init__(self):
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_template(self, template_name, **context):
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_template_string(self, template_string, **context):
        """Render template from string."""
        template = Template(template_string)
        return template.render(**context)

    def send_username_reminder(self, user: User):
        email_body = self.render_template(
            "username_reminder.html", username=user.username
        )

        return send_mail(
            to=user.email,
            subject="Groupbite: Bejelentkezési adat emlékeztető",
            body=email_body,
        )

    def send_order(self, order: Order, basket_sum):
        items_by_category = {}
        all_items = []
        for item in basket_sum.values():
            category = item["category"]
            if category not in items_by_category:
                items_by_category[category] = []
            items_by_category[category].append(item)
            all_items.append(item)

        template = order.vendor.get_setting_value("auto_email_order_template")
        email_body = self.render_template_string(
            template, order=order, basket=all_items, categories=items_by_category
        )

        template = order.vendor.get_setting_value("auto_email_subject")
        email_subject = self.render_template_string(
            template, order=order, vendor=order.vendor
        )
        return send_mail(
            to=order.vendor.get_setting_value("auto_email_order_to"),
            subject=email_subject,
            body=email_body,
            cc=order.vendor.get_setting_value("auto_email_order_cc"),
        )

    def send_test_mail(self, to: list[str], settings: dict):
        email_body = self.render_template("test_email.html")

        return send_mail(
            to=to,
            subject="A message from GroupBite",
            body=email_body,
            settings=settings,
        )


def send_mail(to: list, subject: str, body, cc: list = [], settings=None):
    with get_session() as db:
        setting_repo = SettingRepository(db)
        sender_email = setting_repo.get_value_by_key("smtp_sender_email")
        smtp_server = setting_repo.get_value_by_key("smtp_address")
        smtp_port = setting_repo.get_value_by_key("smtp_port")
        smtp_user = setting_repo.get_value_by_key("smtp_user")
        smtp_password = decrypt_value(setting_repo.get_value_by_key("smtp_password"))
        smtp_security = setting_repo.get_value_by_key("smtp_security")

    if settings != None:
        sender_email = settings["smtp_sender_email"]
        smtp_server = settings["smtp_address"]
        smtp_port = settings["smtp_port"]
        smtp_user = settings["smtp_user"]
        smtp_password = settings["smtp_password"]
        smtp_security = settings["smtp_security"]

    if sender_email == "":
        return False, "sender_email can not be empty"
    if smtp_server == "":
        return False, "smtp_server can not be empty"
    if smtp_port == "":
        return False, "smpt_port can not be empty"

        # Create the email message
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = ", ".join(to)
    msg["Cc"] = ", ".join(cc)
    msg["Subject"] = subject
    to_addresses = to + cc

    # Attach the email body
    msg.attach(MIMEText(body, "plain"))
    msg.attach(MIMEText(body, "html"))

    # Try to log in to server and send email
    try:
        if smtp_port == 465 or smtp_security == "ssl":
            # Use SSL for port 465
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            logging.info("SSL mail in use")
        else:
            # Use non-SSL connection first
            server = smtplib.SMTP(smtp_server, smtp_port)
            if smtp_port == 587 or smtp_security == "tls":
                # Upgrade to a secure connection using STARTTLS for port 587
                server.starttls()
                logging.info("TLS mail in use")

        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, to_addresses, msg.as_string())
        logging.info("Sending mail")
        success, error = True, None
    except Exception as e:
        success, error = False, str(e)
        # Print any error messages to stdout
        logging.error(e)
    finally:
        server.quit()
    return success, error
