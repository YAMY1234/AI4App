import smtplib
from email.mime.text import MIMEText


def send_email(subject, body, recipient_email):
    try:
        sender_email = "yamy1234@foxmail.com"
        sender_password = "ryhattpwdsgedjha"
        # uxswkhfxgkomecff

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Using SMTP service with SSL
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
    except:
        with open("email_log.txt", "a") as log_file:
            log_file.write(f"Email sending failed: {subject} | {body}\n")
