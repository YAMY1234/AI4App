import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_email(subject, body, recipient_email, attachment_path=None):
    if recipient_email is None:
        return
    try:
        sender_email = "yamy1234@foxmail.com"
        sender_password = "ryhattpwdsgedjha"

        # Create a multipart message
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        # Attach the body of the email as MIMEText
        msg.attach(MIMEText(body, 'plain'))

        # Check if there is an attachment
        if attachment_path:
            # Open the file to be sent
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', "attachment; filename= %s" % attachment_path.split("/")[-1])
                msg.attach(part)

        # Using SMTP service with SSL
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
    except Exception as e:
        with open("email_log.txt", "a") as log_file:
            log_file.write(f"Email sending failed: {subject} | {body} | {str(e)}\n")


def test_send_email_with_attachment():
    subject = "Important: Changes Document"
    body = "Please find attached the changes document for your review."
    recipient_email = "yamy12344@gmail.com"
    attachment_path = "/Users/liyangmin/PycharmProjects/AI4App/DDLNotifier/2024-06-02 12-changes.xlsx"

    send_email(subject, body, recipient_email, attachment_path)
    # send_email(subject, body, recipient_email)
    print("Test email sent with attachment.")


# Run the test case
if __name__ == "__main__":
    test_send_email_with_attachment()
