from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
from urllib.parse import quote

from models import Configuracao


def _get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    config = Configuracao.query.filter_by(chave=key).first()
    return config.valor if config else default


def _get_email_config() -> Dict[str, Optional[str]]:
    return {
        "host": _get_config_value("email_host"),
        "port": _get_config_value("email_port"),
        "user": _get_config_value("email_user"),
        "password": _get_config_value("email_password"),
        "from": _get_config_value("email_from", _get_config_value("email_user")),
        "vendor": _get_config_value("email_site", "pastaartencanto@gmail.com"),
        "use_tls": _get_config_value("email_use_tls", "true"),
    }


def _format_phone_whatsapp(phone_raw: Optional[str]) -> str:
    if not phone_raw:
        return ""
    digits = "".join(ch for ch in phone_raw if ch.isdigit())
    if not digits.startswith("55"):
        digits = "55" + digits
    return digits


def _generate_items_html(pedido) -> str:
    parts = []
    for item in pedido.itens:
        sabor_info = f" ({item.sabor_selecionado})" if item.sabor_selecionado else ""
        parts.append(f"<p>• {item.doce.nome}{sabor_info} - {item.quantidade}x - R$ {float(item.preco_total):.2f}</p>")
    return "".join(parts)


def _generate_vendor_whatsapp_message(pedido) -> str:
    message = f"🎉 *Pasta Art Encanto* - Pedido #{pedido.numero_pedido}\n\n"
    message += f"Olá {pedido.usuario.nome}! 😊\n\n"
    message += "Recebemos seu pedido com sucesso!\n\n"
    message += "📋 *Resumo do pedido:*\n"
    for item in pedido.itens:
        sabor_info = f" ({item.sabor_selecionado})" if item.sabor_selecionado else ""
        message += f"• {item.doce.nome}{sabor_info} - {item.quantidade}x - R$ {float(item.preco_total):.2f}\n"
    message += f"\n💰 *Total:* R$ {float(pedido.total):.2f}\n\n"
    message += "📍 Entrega/Retirada: *A combinar*\n"
    message += "💳 Formas de pagamento: *PIX, Dinheiro ou Cartão*\n"
    return message


def _build_client_email_html(pedido) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset=\"UTF-8\">
        <title>Pedido Confirmado - Pasta Art Encanto</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #ff6b9d, #c44569); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .order-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #ff6b9d; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; }}
        </style>
    </head>
    <body>
        <div class=\"container\">
            <div class=\"header\">
                <h1>🍰 Pasta Art Encanto</h1>
                <h2>Pedido #{pedido.numero_pedido} Confirmado!</h2>
            </div>
            <div class=\"content\">
                <h3>Olá {pedido.usuario.nome}! 😊</h3>
                <p>Recebemos seu pedido com sucesso! Agradecemos pela confiança.</p>
                <div class=\"order-details\">
                    <h4>📋 Resumo do seu pedido:</h4>
                    {_generate_items_html(pedido)}
                    <hr>
                    <h3>💰 Total: R$ {float(pedido.total):.2f}</h3>
                </div>
                <p><strong>📍 Entrega/Retirada:</strong> A combinar</p>
                <p><strong>💳 Formas de pagamento:</strong> PIX, Dinheiro ou Cartão</p>
                <p>Entraremos em contato por WhatsApp para acertar os detalhes.</p>
            </div>
            <div class=\"footer\">
                <p>Pasta Art Encanto - Doces Artesanais</p>
            </div>
        </div>
    </body>
    </html>
    """


def _build_vendor_email_html(pedido) -> str:
    phone = _format_phone_whatsapp(pedido.usuario.telefone)
    wa_message = _generate_vendor_whatsapp_message(pedido)
    wa_url = f"https://wa.me/{phone}?text={quote(wa_message)}" if phone else ""

    endereco = pedido.usuario.get_endereco_formatado() or "Não informado"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset=\"UTF-8\">
        <title>Novo Pedido #{pedido.numero_pedido} - Pasta Art Encanto</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #ff6b9d, #c44569); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .order-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #ff6b9d; }}
            .customer-info {{ background: #e8f4fd; padding: 20px; margin: 20px 0; border-radius: 8px; }}
            .whatsapp-btn {{ background: #25d366; color: white; padding: 12px 18px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 16px 0; font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; }}
        </style>
    </head>
    <body>
        <div class=\"container\">
            <div class=\"header\">
                <h1>🍰 Pasta Art Encanto</h1>
                <h2>Novo Pedido #{pedido.numero_pedido}</h2>
            </div>
            <div class=\"content\">
                <h3>🎉 Novo pedido recebido!</h3>
                <div class=\"customer-info\">
                    <h4>👤 Informações do Cliente:</h4>
                    <p><strong>Nome:</strong> {pedido.usuario.nome}</p>
                    <p><strong>Email:</strong> {pedido.usuario.email}</p>
                    <p><strong>Telefone:</strong> {pedido.usuario.telefone or 'Não informado'}</p>
                    <p><strong>Endereço:</strong> {endereco}</p>
                    <p><strong>Data do pedido:</strong> {pedido.data_pedido.strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
                <div class=\"order-details\">
                    <h4>📋 Itens do Pedido:</h4>
                    {_generate_items_html(pedido)}
                    <hr>
                    <h3>💰 Total: R$ {float(pedido.total):.2f}</h3>
                </div>
                {f'<div style="text-align:center;"><a href="{wa_url}" class="whatsapp-btn" target="_blank">💬 Enviar Confirmação via WhatsApp</a></div>' if wa_url else ''}
                <p><strong>Dica:</strong> Use o botão acima para enviar a confirmação ao cliente.</p>
            </div>
            <div class=\"footer\">
                <p>Pasta Art Encanto - Painel Administrativo</p>
            </div>
        </div>
    </body>
    </html>
    """


def _send_email(destinatario: str, assunto: str, html_content: str) -> bool:
    cfg = _get_email_config()

    host = cfg.get("host")
    port = int(cfg.get("port") or 587)
    user = cfg.get("user")
    password = cfg.get("password")
    sender = cfg.get("from") or user
    use_tls = (cfg.get("use_tls") or "true").lower() != "false"

    if not (host and port and user and password and sender):
        print("[EMAIL] Configuração de SMTP incompleta. Emails não enviados.")
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = assunto
        msg['From'] = sender
        msg['To'] = destinatario
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        with smtplib.SMTP(host, port) as server:
            if use_tls:
                server.starttls()
            server.login(user, password)
            server.send_message(msg)

        print(f"[EMAIL] Enviado para {destinatario}")
        return True
    except Exception as e:
        print(f"[EMAIL] Erro ao enviar para {destinatario}: {e}")
        return False


def send_order_emails(pedido) -> bool:
    """Envia email para cliente e vendedora. Retorna True se pelo menos um envio foi bem-sucedido."""
    cfg = _get_email_config()
    vendor_email = cfg.get("vendor") or "pastaartencanto@gmail.com"

    client_ok = _send_email(
        destinatario=pedido.usuario.email,
        assunto=f"Pedido #{pedido.numero_pedido} Confirmado - Pasta Art Encanto",
        html_content=_build_client_email_html(pedido)
    ) if pedido.usuario and pedido.usuario.email else False

    vendor_ok = _send_email(
        destinatario=vendor_email,
        assunto=f"Novo Pedido #{pedido.numero_pedido} - Pasta Art Encanto",
        html_content=_build_vendor_email_html(pedido)
    )

    return bool(client_ok or vendor_ok)


