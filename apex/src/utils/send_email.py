import logging
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

from src.config import get_settings
from src.utils.report_html import sanitize_report_html


logger = logging.getLogger(__name__)
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailSendError(RuntimeError):
    pass


def is_valid_email(value):
    if not value:
        return False
    _, address = parseaddr(value.strip())
    return bool(address and EMAIL_PATTERN.match(address))


def build_apex_email_html(report_html, intro_message=None):
    safe_report = sanitize_report_html(report_html)
    safe_intro = sanitize_report_html((intro_message or "").replace("\n", "<br>"))
    intro_block = f'<div class="intro">{safe_intro}</div>' if safe_intro else ""
    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <style>
            body {{ margin:0; padding:0; background:#f4f5f8; color:#202331; font-family:Arial, sans-serif; }}
            .wrap {{ width:100%; padding:24px 0; background:#f4f5f8; }}
            .panel {{ max-width:900px; margin:0 auto; background:#ffffff; border:1px solid #dfe2eb; }}
            .header {{ padding:28px 32px; background:#504cab; color:#ffffff; }}
            .brand {{ margin:0; font-size:24px; line-height:30px; font-weight:700; }}
            .subtitle {{ margin:6px 0 0; font-size:14px; line-height:20px; color:#eef0ff; }}
            .content {{ padding:28px 32px; }}
            .intro {{ border-left:4px solid #12a594; margin-bottom:24px; padding:12px 16px; background:#f0fbf9; }}
            .footer {{ padding:20px 32px; background:#202331; color:#ffffff; font-size:13px; line-height:18px; }}
            a {{ color:#504cab; }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <div class="panel">
                <div class="header">
                    <h1 class="brand">APEX</h1>
                    <p class="subtitle">Relatório de Monitoramento de Mídia</p>
                </div>
                <div class="content">{intro_block}{safe_report}</div>
                <div class="footer">
                    Apex Conteudo Estrategico<br>
                    <a href="https://apexconteudo.com.br/" style="color:#ffffff;">apexconteudo.com.br</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


class SendEmail:
    def __init__(self, smtp_login, smtp_password):
        settings = get_settings()
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_login = smtp_login
        self.smtp_password = smtp_password
        self.timeout = settings.smtp_timeout_seconds

    def send_email_to(self, response, email, subject=None, intro_message=None):
        if not is_valid_email(email):
            raise EmailSendError("Email de destino inválido.")
        if not self.smtp_login or not self.smtp_password:
            raise EmailSendError("Email ou senha SMTP não cadastrados.")

        msg = MIMEMultipart()
        msg["Subject"] = subject or "[APEX] Relatório de monitoramento"
        msg["From"] = formataddr(("Apex", self.smtp_login))
        msg["To"] = email.strip()
        msg.attach(MIMEText(build_apex_email_html(response, intro_message=intro_message), "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout) as server:
                server.starttls()
                server.login(self.smtp_login, self.smtp_password)
                server.sendmail(self.smtp_login, [email.strip()], msg.as_string())
        except (smtplib.SMTPException, OSError) as exc:
            logger.exception("Falha ao enviar email Apex para %s", email)
            raise EmailSendError("Não foi possível enviar o email. Verifique as credenciais SMTP e tente novamente.") from exc

        logger.info("Email Apex enviado para %s", email)
        return True
