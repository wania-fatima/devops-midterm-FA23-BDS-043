import json, os, smtplib, sys
from email.message import EmailMessage
from pathlib import Path

status = sys.argv[1] if len(sys.argv) > 1 else 'UNKNOWN'
sid = json.loads(Path('config.json').read_text())['student_id']
try:
    m = json.loads(Path('artifacts/metrics.json').read_text())
except Exception:
    m = {}
user = os.environ['SMTP_USER']
pw = os.environ['SMTP_PASS'].replace(' ', '')
to = 'qasimalik@gmail.com'
msg = EmailMessage()
msg['From'] = user
msg['To'] = to
msg['Subject'] = f"[{sid}] Jenkins build #{os.environ.get('BUILD_NUMBER', '?')} {status}"
msg.set_content(
    f"Student Reg No: {sid}\nBuild status: {status}\n"
    f"Build URL: {os.environ.get('BUILD_URL', '')}\n"
    f"Git SHA: {os.environ.get('GIT_COMMIT', '')}\n"
    f"Accuracy: {m.get('accuracy')}\nTraining rows: {m.get('training_rows')}\n"
    f"Model version: {m.get('model_version')}\n"
    f"Metrics: http://15.207.240.78:8000/metrics\n")
with smtplib.SMTP('smtp.gmail.com', 587, timeout=60) as s:
    s.starttls()
    s.login(user, pw)
    s.send_message(msg, to_addrs=[to, user])
print('Email sent to', to)
