import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.entities.setting import Setting
import logging



def send_mail(to, subject, body, settings=None):

    sender_email = Setting.get_value_by_key("smtp_sender_email")
    smtp_server = Setting.get_value_by_key("smtp_address")
    smtp_port = Setting.get_value_by_key("smtp_port")
    smtp_user = Setting.get_value_by_key("smtp_user")
    smtp_password = Setting.get_value_by_key("smtp_password")

    if settings != None:
        sender_email = settings["sender_email"]
        smtp_server = settings["smtp_address"]
        smtp_port = settings["smtp_port"]
        smtp_user = settings["smtp_user"]
        smtp_password = settings["smtp_password"]

    if sender_email == "" :
        return False, "sender_email can not be empty"
    if smtp_server == "":
        return False, "smtp_server can not be empty"
    if smtp_port == "":
        return False, "smpt_port can not be empty"


        # Create the email message
    msg = MIMEMultipart("alternative")
    msg['From'] = sender_email
    msg['To'] = to
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body.replace("\r\n", "<br>"), 'html'))
    msg.attach(MIMEText(body.replace("<br>", "\r\n"), 'plain'))

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        if smtp_port == 465:
            # Use SSL for port 465
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            # Use non-SSL connection first
            server = smtplib.SMTP(smtp_server, smtp_port)
            if smtp_port == 587:
                # Upgrade to a secure connection using STARTTLS for port 587
                server.starttls()

        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, to, msg.as_string())
        success, error = True, None
    except Exception as e:
        success, error = False, str(e)
        # Print any error messages to stdout
        logging.error(e)
    finally:
        server.quit()
        return success, error
