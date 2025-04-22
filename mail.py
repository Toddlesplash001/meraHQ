import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email = "ayaan.gautam@myhq.in"
to_email = "ayaangautam@gmail.com"
cc_email = ["kuwarjain394@gmail.com", "devanshvashisht22@gmail.com"]
app_password = "jmzq bmmu jhmo aviw"

# Combine all recipients for sending
to_list = [to_email] + cc_email

# Create the email
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = to_email
msg["Cc"] = ", ".join(cc_email)
msg["Subject"] = "Test Email with CC"

# Email body
body = "This is a test email with CC recipients."
msg.attach(MIMEText(body, "plain"))

# Send the email
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, to_list, msg.as_string())
