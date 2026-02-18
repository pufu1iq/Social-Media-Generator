import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import getpass

def send_email():
    print("=== Email Report Sender ===")
    print("This script sends 'created_accounts_report.xlsx' to davidpufu@gmail.com.")
    print("You need a sender Gmail account and an App Password.")
    print("If you don't have an App Password, go to Google Account > Security > 2-Step Verification > App Passwords.")
    
    sender_email = input("\nEnter your Gmail address (Sender): ")
    sender_password = getpass.getpass("Enter your Gmail App Password: ")
    receiver_email = "davidpufu@gmail.com"
    
    subject = "Social Media Accounts Report"
    body = "Attached is the latest report of created social media accounts."
    filename = "created_accounts_report.xlsx"

    if not os.path.exists(filename):
        print(f"Error: {filename} not found in the current directory.")
        return

    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Attachment
    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    message.attach(part)

    # Send
    try:
        print("Connecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        print(f"Sending email to {receiver_email}...")
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

if __name__ == "__main__":
    send_email()
