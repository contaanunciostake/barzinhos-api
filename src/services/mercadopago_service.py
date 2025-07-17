import mercadopago
import json
from datetime import datetime, timedelta
from src.models.payment_config import PaymentConfig
from src.models.payment import Payment
from src.models.user import User

class MercadoPagoService:
    def __init__(self):
        self.config = PaymentConfig.get_active_config()
        self.sdk = None
        self._initialize_sdk()
    
    def _initialize_sdk(self):
        """Inicializa o SDK do MercadoPago com as credenciais atuais."""
        credentials = self.config.get_current_credentials()
        if credentials['access_token']:
            # Descriptografar o token (implementação simplificada)
            # Em produção, usar uma criptografia mais robusta
            access_token = credentials['access_token']
            self.sdk = mercadopago.SDK(access_token)
        else:
            raise ValueError("Access token do MercadoPago não configurado")
    
    def create_preference(self, user_id, plan_id, success_url=None, failure_url=None, pending_url=None):
        """Cria uma preferência de pagamento no MercadoPago."""
        try:
            user = User.query.get(user_id)
            if not user:
                raise ValueError("Usuário não encontrado")
            
            plan_price = self.config.get_plan_price(plan_id)
            if plan_price <= 0:
                raise ValueError("Plano inválido ou gratuito")
            
            # Criar registro de pagamento
            payment = Payment(
                user_id=user_id,
                plan_id=plan_id,
                amount=plan_price,
                currency='BRL',
                status='pending',
                description=f'Assinatura {plan_id.title()} - {user.username}',
                external_reference=f'user_{user_id}_plan_{plan_id}_{int(datetime.utcnow().timestamp())}'
            )
            
            from src.models.base import db
            db.session.add(payment)
            db.session.flush()  # Para obter o ID
            
            # Configurar preferência
            preference_data = {
                "items": [
                    {
                        "title": f"Plano {plan_id.title()} - Barzinhos",
                        "description": f"Assinatura mensal do plano {plan_id.title()}",
                        "quantity": 1,
                        "currency_id": "BRL",
                        "unit_price": plan_price
                    }
                ],
                "payer": {
                    "name": user.username,
                    "email": user.email
                },
                "external_reference": payment.external_reference,
                "notification_url": self.config.webhook_url,
                "auto_return": "approved",
                "back_urls": {
                    "success": success_url or "https://seu-site.com/success",
                    "failure": failure_url or "https://seu-site.com/failure", 
                    "pending": pending_url or "https://seu-site.com/pending"
                },
                "expires": True,
                "expiration_date_from": datetime.utcnow().isoformat(),
                "expiration_date_to": (datetime.utcnow() + timedelta(hours=24)).isoformat()
            }
            
            # Criar preferência no MercadoPago
            preference_response = self.sdk.preference().create(preference_data)
            
            if preference_response["status"] == 201:
                preference = preference_response["response"]
                
                # Atualizar pagamento com dados da preferência
                payment.mp_preference_id = preference["id"]
                db.session.commit()
                
                return {
                    "success": True,
                    "preference_id": preference["id"],
                    "init_point": preference["init_point"],
                    "sandbox_init_point": preference.get("sandbox_init_point"),
                    "payment_id": payment.id,
                    "external_reference": payment.external_reference
                }
            else:
                db.session.rollback()
                return {
                    "success": False,
                    "error": "Erro ao criar preferência no MercadoPago",
                    "details": preference_response
                }
                
        except Exception as e:
            from src.models.base import db
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_payment_info(self, payment_id):
        """Busca informações de um pagamento no MercadoPago."""
        try:
            payment_response = self.sdk.payment().get(payment_id)
            
            if payment_response["status"] == 200:
                return {
                    "success": True,
                    "payment": payment_response["response"]
                }
            else:
                return {
                    "success": False,
                    "error": "Pagamento não encontrado",
                    "details": payment_response
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_webhook_notification(self, notification_data):
        """Processa notificação do webhook do MercadoPago."""
        try:
            notification_type = notification_data.get("type")
            
            if notification_type == "payment":
                payment_id = notification_data.get("data", {}).get("id")
                if payment_id:
                    return self._process_payment_notification(payment_id)
            
            elif notification_type == "merchant_order":
                order_id = notification_data.get("data", {}).get("id")
                if order_id:
                    return self._process_merchant_order_notification(order_id)
            
            return {"success": True, "message": "Notificação processada"}
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_payment_notification(self, mp_payment_id):
        """Processa notificação de pagamento."""
        try:
            # Buscar informações do pagamento no MercadoPago
            payment_info = self.get_payment_info(mp_payment_id)
            
            if not payment_info["success"]:
                return payment_info
            
            mp_payment = payment_info["payment"]
            
            # Buscar pagamento local
            payment = Payment.get_by_mp_payment_id(mp_payment_id)
            
            if not payment:
                # Criar pagamento se não existir (caso de webhook antes da criação local)
                external_ref = mp_payment.get("external_reference", "")
                if external_ref:
                    # Extrair user_id da referência externa
                    try:
                        user_id = int(external_ref.split("_")[1])
                        plan_id = external_ref.split("_")[3]
                        
                        payment = Payment(
                            user_id=user_id,
                            plan_id=plan_id,
                            amount=mp_payment["transaction_amount"],
                            currency=mp_payment["currency_id"],
                            mp_payment_id=str(mp_payment_id),
                            external_reference=external_ref
                        )
                        
                        from src.models.base import db
                        db.session.add(payment)
                    except:
                        return {"success": False, "error": "Referência externa inválida"}
            
            # Atualizar dados do pagamento
            payment.mp_payment_id = str(mp_payment_id)
            payment.status = mp_payment["status"]
            payment.status_detail = mp_payment.get("status_detail")
            payment.payment_method = mp_payment.get("payment_method_id")
            payment.payment_type = mp_payment.get("payment_type_id")
            payment.webhook_data = json.dumps(mp_payment)
            
            # Se aprovado, ativar assinatura
            if mp_payment["status"] == "approved":
                subscription = payment.approve_payment()
                
            from src.models.base import db
            db.session.commit()
            
            return {
                "success": True,
                "payment_id": payment.id,
                "status": payment.status
            }
            
        except Exception as e:
            from src.models.base import db
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_merchant_order_notification(self, order_id):
        """Processa notificação de merchant order."""
        try:
            order_response = self.sdk.merchant_order().get(order_id)
            
            if order_response["status"] == 200:
                order = order_response["response"]
                
                # Processar pagamentos da ordem
                for payment_data in order.get("payments", []):
                    if payment_data.get("status") == "approved":
                        self._process_payment_notification(payment_data["id"])
                
                return {"success": True, "order_id": order_id}
            else:
                return {
                    "success": False,
                    "error": "Ordem não encontrada",
                    "details": order_response
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def validate_credentials(self, access_token, is_production=False):
        """Valida as credenciais do MercadoPago."""
        try:
            test_sdk = mercadopago.SDK(access_token)
            
            # Fazer uma requisição de teste
            response = test_sdk.payment().search()
            
            return response["status"] in [200, 201]
            
        except Exception as e:
            return False

