import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SendEmail:
    def __init__(self,smtp_login, smtp_password):
        # Configurações do servidor SMTP do Gmail
        self.smtp_server= 'smtp.gmail.com'
        self.smtp_port= 587  # Porta padrão para TLS
        self.smtp_login= smtp_login # Seu endereço de e-mail do Gmail
        self.smtp_password = smtp_password#'azqvruvuetpsityw'  # Sua senha do Gmail 

    def send_email_to(self, response, email):
    # Conecte-se ao servidor SMTP e envie a mensagem
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_login, self.smtp_password)
            
            
            msg = MIMEMultipart()
            msg['Subject'] = '[APEX] Resultado do relatório GPT'
            msg['From'] = self.smtp_login
            msg['To'] = email

            html = f"""
            <!DOCTYPE html>
            <html lang="pt-br"  xmlns:o="urn:schemas-microsoft-com:office:office">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width,initial-scale=1">
                <meta name="x-apple-disable-message-reformatting">
                <title></title>
                <!--[if mso]>
                <noscript>
                <xml>
                    <o:OfficeDocumentSettings>
                    <o:PixelsPerInch>96</o:PixelsPerInch>
                    </o:OfficeDocumentSettings>
                </xml>
                </noscript>
                <![endif]-->
                <style>
                table, td, div, h1, p {{font-family: Arial, sans-serif;}}
                </style>
            </head>
            <body style="margin:0;padding:0;">
                <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;background:#ffffff;">
                <tr>
                    <td align="center" style="padding:0;">
                    <table role="presentation" style="width:900px;border-collapse:collapse;border:1px solid #cccccc;border-spacing:0;text-align:left;">
                        <tr>
                        <td style="padding:18px 30px 42px 30px;">
                            <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;">
                            <tr>
                                <td align="center" style="padding:40px 0 0 0;background:#ffffff;">
                                <img src="https://i.ibb.co/DCXMwvw/thambnail.jpg" alt="" width="100%" style="height:auto;display:block;" />
                                </td>
                            </tr>
                            <tr>
                                <td style="padding:0 0 0 0;color:#153643;">
                                <h1>
                                Relatório de Monitoramento de Mídia APEX
                                </h1>
                                <br>
                                {response}                    
                                </td>
                            </tr>
                            </table>
                        </td>
                        </tr>
                        <tr>
                        <td style="padding:30px;background:#504cab;">
                            <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;font-size:9px;font-family:Arial,sans-serif;">
                            <tr>
                                <td style="padding:0;width:50%;" align="left">
                                <p style="margin:0;font-size:14px;line-height:16px;font-family:Arial,sans-serif;color:#ffffff;">
                                    &reg; 2023 por APEX, todos os direitos reservados<br/><a href="https://apexconteudo.com.br/" style="color:#ffffff;text-decoration:underline;">apexconteudo.com.br</a>
                                </p>
                                </td>
                                <td style="padding:0;width:50%;" align="right">
                                <table role="presentation" style="border-collapse:collapse;border:0;border-spacing:0;">
                                    <tr>
                                    <td style="padding:0 0 0 10px;width:38px;">
                                        <a href="https://www.linkedin.com/company/apex-conte%C3%BAdo-estrat%C3%A9gico/" style="color:#504cab;"><img src="https://i.ibb.co/FYgRQLF/linkedin-icon.png" alt="Linkedin" width="38" style="height:auto;display:block;border:0;" /></a>
                                    </td>
                                    <td style="padding:0 0 0 10px;width:38px;">
                                        <a href="https://www.instagram.com/apexagencia/" style="color:#504cab;"><img src="https://i.ibb.co/PWQbddz/instagram-icon.png" alt="Instagram" width="38" style="height:auto;display:block;border:0;" /></a>
                                    </td>
                                    </tr>
                                </table>
                                </td>
                            </tr>
                            </table>
                        </td>
                        </tr>
                    </table>
                    </td>
                </tr>
                </table>
            </body>
            </html>
            """
            try:
                part = MIMEText(html, 'html')
                msg.attach(part)
                server.sendmail(self.smtp_login, email, msg.as_string())
                return True
            except:
                return False