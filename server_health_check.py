import psutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# 发送邮件函数
def send_email(subject, body, recipient_email, attachment_path=None):
    if recipient_email is None:
        return
    try:
        sender_email = "yamy1234@foxmail.com"
        sender_password = "ryhattpwdsgedjha"

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg.attach(MIMEText(body, 'plain'))

        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f"attachment; filename= {attachment_path.split('/')[-1]}")
                msg.attach(part)

        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
    except Exception as e:
        with open("email_log.txt", "a") as log_file:
            log_file.write(f"Email sending failed: {subject} | {body} | {str(e)}\n")

# 检查内存和磁盘使用情况
def check_system_resources():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    # 定义异常阈值
    memory_threshold = 90  # 内存使用超过80%
    disk_threshold = 90    # 磁盘使用超过90%

    # 检查是否超出阈值
    issues = []
    if memory.percent > memory_threshold:
        issues.append(f"Memory usage is high: {memory.percent}%")

    if disk.percent > disk_threshold:
        issues.append(f"Disk usage is high: {disk.percent}% on root partition")

    # 如果有异常，发送邮件
    if issues:
        subject = "System Resource Alert"
        body = "The following resource issues were detected:\n\n" + "\n".join(issues)
        send_email(subject, body, "yamy12344@gmail.com")

# 主函数
if __name__ == "__main__":
    check_system_resources()