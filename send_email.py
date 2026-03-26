import smtplib
from email.message import EmailMessage

def send_email():

    # ---------------- CONFIG ----------------
    SENDER_EMAIL = "medicallmanav@gmail.com"
    APP_PASSWORD = "qpbz agxs ufgc mpqh"
    RECEIVER_EMAIL = "acharyamanav7@gmail.com"

    # ---------------- CREATE EMAIL ----------------
    msg = EmailMessage()
    msg["Subject"] = "Daily Stock Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    msg.set_content("Attached is your daily stock analytics report.")

    # Attach PDF
    with open("report.pdf", "rb") as f:
        file_data = f.read()
        file_name = "report.pdf"

    msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

    # ---------------- SEND EMAIL ----------------
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)

        print("✅ Email sent successfully!")

    except Exception as e:
        print("❌ Failed to send email:", e)

if __name__ == '__main__':
    send_email()
