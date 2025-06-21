from flask import Blueprint, request, jsonify
import datetime
import json

automation_bp = Blueprint('automation', __name__)

# Simulação de integração com WhatsApp
@automation_bp.route('/send-whatsapp', methods=['POST'])
def send_whatsapp():
    """
    Simula o envio de mensagem via WhatsApp
    """
    try:
        data = request.get_json()
        phone = data.get('phone')
        message = data.get('message')
        establishment_name = data.get('establishment_name', '')
        
        if not phone or not message:
            return jsonify({
                'success': False,
                'error': 'Telefone e mensagem são obrigatórios'
            }), 400
        
        # Simular envio (em produção, aqui seria a integração real com WhatsApp API)
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'phone': phone,
            'message': message,
            'establishment': establishment_name,
            'status': 'sent'
        }
        
        # Log da mensagem enviada
        print(f"[WhatsApp] Mensagem enviada para {phone}: {message}")
        
        return jsonify({
            'success': True,
            'message': 'Mensagem enviada com sucesso',
            'data': log_entry
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/welcome-message', methods=['POST'])
def send_welcome_message():
    """
    Envia mensagem de boas-vindas para estabelecimento recém-cadastrado
    """
    try:
        data = request.get_json()
        establishment_id = data.get('establishment_id')
        phone = data.get('phone')
        establishment_name = data.get('establishment_name')
        
        if not all([establishment_id, phone, establishment_name]):
            return jsonify({
                'success': False,
                'error': 'Dados incompletos'
            }), 400
        
        # Mensagem de boas-vindas personalizada
        welcome_message = f"""
🎉 Bem-vindo ao Barzinhos, {establishment_name}!

Seu estabelecimento foi cadastrado com sucesso e está aguardando aprovação.

📋 Próximos passos:
• Nossa equipe irá revisar seu cadastro
• Você receberá uma notificação quando for aprovado
• Após aprovação, seu estabelecimento aparecerá na plataforma

💡 Dicas:
• Mantenha suas informações sempre atualizadas
• Responda rapidamente aos clientes
• Use fotos atrativas do seu estabelecimento

Em caso de dúvidas, entre em contato conosco!

Equipe Barzinhos 🍻
        """.strip()
        
        # Simular envio da mensagem
        result = send_whatsapp_internal(phone, welcome_message, establishment_name)
        
        return jsonify({
            'success': True,
            'message': 'Mensagem de boas-vindas enviada',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/approval-notification', methods=['POST'])
def send_approval_notification():
    """
    Envia notificação de aprovação para estabelecimento
    """
    try:
        data = request.get_json()
        establishment_id = data.get('establishment_id')
        phone = data.get('phone')
        establishment_name = data.get('establishment_name')
        approved = data.get('approved', True)
        
        if not all([establishment_id, phone, establishment_name]):
            return jsonify({
                'success': False,
                'error': 'Dados incompletos'
            }), 400
        
        if approved:
            approval_message = f"""
✅ Parabéns, {establishment_name}!

Seu estabelecimento foi APROVADO e já está disponível na plataforma Barzinhos!

🚀 Agora você pode:
• Ser encontrado por milhares de clientes
• Receber avaliações e comentários
• Gerenciar seu perfil online

🔗 Acesse: https://barzinhos.com.br

Desejamos muito sucesso!

Equipe Barzinhos 🍻
            """.strip()
        else:
            approval_message = f"""
❌ Olá, {establishment_name}

Infelizmente seu cadastro não foi aprovado desta vez.

📝 Possíveis motivos:
• Informações incompletas
• Documentação pendente
• Não atende aos critérios da plataforma

💬 Entre em contato conosco para mais informações e tente novamente.

Equipe Barzinhos 🍻
            """.strip()
        
        # Simular envio da mensagem
        result = send_whatsapp_internal(phone, approval_message, establishment_name)
        
        return jsonify({
            'success': True,
            'message': f'Notificação de {"aprovação" if approved else "rejeição"} enviada',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/renewal-reminder', methods=['POST'])
def send_renewal_reminder():
    """
    Envia lembrete de renovação de assinatura
    """
    try:
        data = request.get_json()
        establishment_id = data.get('establishment_id')
        phone = data.get('phone')
        establishment_name = data.get('establishment_name')
        plan_type = data.get('plan_type', 'Bronze')
        days_until_expiry = data.get('days_until_expiry', 7)
        
        if not all([establishment_id, phone, establishment_name]):
            return jsonify({
                'success': False,
                'error': 'Dados incompletos'
            }), 400
        
        renewal_message = f"""
⏰ Lembrete de Renovação - {establishment_name}

Sua assinatura do plano {plan_type} vence em {days_until_expiry} dias.

💳 Para continuar aproveitando todos os benefícios:
• Acesse seu painel de controle
• Renove sua assinatura
• Mantenha sua visibilidade na plataforma

🔗 Renovar agora: https://barzinhos.com.br/renovar

Não perca clientes! Renove hoje mesmo.

Equipe Barzinhos 🍻
        """.strip()
        
        # Simular envio da mensagem
        result = send_whatsapp_internal(phone, renewal_message, establishment_name)
        
        return jsonify({
            'success': True,
            'message': 'Lembrete de renovação enviado',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@automation_bp.route('/upsell-message', methods=['POST'])
def send_upsell_message():
    """
    Envia mensagem de upsell baseada no desempenho
    """
    try:
        data = request.get_json()
        establishment_id = data.get('establishment_id')
        phone = data.get('phone')
        establishment_name = data.get('establishment_name')
        current_plan = data.get('current_plan', 'Bronze')
        views_count = data.get('views_count', 0)
        
        if not all([establishment_id, phone, establishment_name]):
            return jsonify({
                'success': False,
                'error': 'Dados incompletos'
            }), 400
        
        # Determinar plano sugerido
        if current_plan == 'Bronze':
            suggested_plan = 'Prata'
            benefits = '5 fotos, destaque por bairro e integração WhatsApp'
        elif current_plan == 'Prata':
            suggested_plan = 'Ouro'
            benefits = 'destaque geral, stories e link Instagram'
        else:
            suggested_plan = 'Premium'
            benefits = 'máxima visibilidade e recursos exclusivos'
        
        upsell_message = f"""
📈 Ótimas notícias, {establishment_name}!

Seu estabelecimento teve {views_count} visualizações este mês! 🎉

💡 Que tal aumentar ainda mais sua visibilidade?

🚀 Upgrade para o plano {suggested_plan}:
• {benefits}
• Mais clientes
• Maior faturamento

🔗 Fazer upgrade: https://barzinhos.com.br/upgrade

Aproveite o momento de alta procura!

Equipe Barzinhos 🍻
        """.strip()
        
        # Simular envio da mensagem
        result = send_whatsapp_internal(phone, upsell_message, establishment_name)
        
        return jsonify({
            'success': True,
            'message': 'Mensagem de upsell enviada',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def send_whatsapp_internal(phone, message, establishment_name):
    """
    Função interna para simular envio de WhatsApp
    """
    log_entry = {
        'timestamp': datetime.datetime.now().isoformat(),
        'phone': phone,
        'message': message,
        'establishment': establishment_name,
        'status': 'sent'
    }
    
    # Log da mensagem enviada
    print(f"[WhatsApp] Mensagem enviada para {phone} ({establishment_name})")
    print(f"Mensagem: {message[:100]}...")
    
    return log_entry

@automation_bp.route('/automation-logs', methods=['GET'])
def get_automation_logs():
    """
    Retorna logs das automações (simulado)
    """
    try:
        # Em produção, isso viria de um banco de dados
        sample_logs = [
            {
                'id': 1,
                'type': 'welcome',
                'establishment': 'Bar do Teste',
                'phone': '5511999999999',
                'timestamp': datetime.datetime.now().isoformat(),
                'status': 'sent'
            },
            {
                'id': 2,
                'type': 'approval',
                'establishment': 'Boteco do João',
                'phone': '5511888888888',
                'timestamp': (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(),
                'status': 'sent'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': sample_logs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

