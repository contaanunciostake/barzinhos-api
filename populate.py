#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo.
Cria usuários admin e estabelecimento, além de 10 estabelecimentos de exemplo.
"""

import os
import sys
import random
from datetime import datetime, timedelta

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.base import db
from src.models.user import User
from src.models.establishment import Establishment, EstablishmentImage
from src.models.review import Review
from src.main import app

def create_users():
    """Cria usuários de exemplo."""
    print("Criando usuários...")
    
    # Usuário admin
    admin = User.query.filter_by(email='admin@barzinhos.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@barzinhos.com',
            role='admin'
        )
        admin.set_password('123456')
        db.session.add(admin)
        print("✓ Usuário admin criado")
    else:
        print("✓ Usuário admin já existe")
    
    # Usuário estabelecimento
    establishment_user = User.query.filter_by(email='bar@exemplo.com').first()
    if not establishment_user:
        establishment_user = User(
            username='bar_exemplo',
            email='bar@exemplo.com',
            role='establishment'
        )
        establishment_user.set_password('123456')
        db.session.add(establishment_user)
        print("✓ Usuário estabelecimento criado")
    else:
        print("✓ Usuário estabelecimento já existe")
    
    db.session.commit()
    return admin, establishment_user

def create_establishments():
    """Cria estabelecimentos de exemplo."""
    print("Criando estabelecimentos...")
    
    # Buscar usuário estabelecimento
    establishment_user = User.query.filter_by(email='bar@exemplo.com').first()
    if not establishment_user:
        print("❌ Usuário estabelecimento não encontrado")
        return
    
    establishments_data = [
        {
            'name': 'Bar do João',
            'description': 'Um bar tradicional com ambiente familiar e as melhores cervejas geladas da cidade.',
            'type': 'Bar',
            'cep': '01310-100',
            'state': 'SP',
            'city': 'São Paulo',
            'neighborhood': 'Bela Vista',
            'address': 'Avenida Paulista, 1000',
            'phone': '(11) 3333-4444',
            'whatsapp': '11999887766',
            'instagram': '@bardojoao',
            'website': 'https://bardojoao.com.br',
            'faixa_etaria': '18+',
            'pet_friendly': True,
            'lgbt_friendly': True,
            'delivery': True,
            'link_delivery': 'https://ifood.com.br/bardojoao',
            'ponto_referencia': 'Próximo ao metrô Trianon-MASP, em frente ao Parque Trianon',
            'como_chegar_transporte': 'Metrô linha verde, estação Trianon-MASP. Ônibus linhas 107M, 2018, 875T',
            'horarios_funcionamento': {
                'segunda': 'Fechado',
                'terca': '18:00-02:00',
                'quarta': '18:00-02:00',
                'quinta': '18:00-02:00',
                'sexta': '18:00-03:00',
                'sabado': '16:00-03:00',
                'domingo': '16:00-00:00'
            },
            'is_approved': True
        },
        {
            'name': 'Restaurante Sabor & Arte',
            'description': 'Culinária contemporânea com ingredientes frescos e pratos autorais.',
            'type': 'Restaurante',
            'cep': '22071-900',
            'state': 'RJ',
            'city': 'Rio de Janeiro',
            'neighborhood': 'Copacabana',
            'address': 'Rua Barata Ribeiro, 500',
            'phone': '(21) 2222-3333',
            'instagram': '@saborearte',
            'faixa_etaria': 'Livre',
            'pet_friendly': False,
            'lgbt_friendly': True,
            'delivery': True,
            'link_delivery': 'https://ubereats.com/saborearte',
            'ponto_referencia': 'A duas quadras da praia de Copacabana, próximo ao Copacabana Palace',
            'como_chegar_transporte': 'Metrô linha 1, estação Cantagalo. Ônibus linhas 415, 435, 474',
            'horarios_funcionamento': {
                'segunda': '12:00-15:00, 19:00-23:00',
                'terca': '12:00-15:00, 19:00-23:00',
                'quarta': '12:00-15:00, 19:00-23:00',
                'quinta': '12:00-15:00, 19:00-23:00',
                'sexta': '12:00-15:00, 19:00-00:00',
                'sabado': '12:00-16:00, 19:00-00:00',
                'domingo': '12:00-22:00'
            },
            'is_approved': True
        },
        {
            'name': 'Pub The Crown',
            'description': 'Pub inglês autêntico com cervejas importadas e música ao vivo.',
            'type': 'Pub',
            'cep': '30112-000',
            'state': 'MG',
            'city': 'Belo Horizonte',
            'neighborhood': 'Centro',
            'address': 'Rua da Bahia, 1200',
            'phone': '(31) 3333-5555',
            'whatsapp': '31988776655',
            'website': 'https://thecrown.com.br',
            'faixa_etaria': '21+',
            'pet_friendly': True,
            'lgbt_friendly': True,
            'delivery': False,
            'ponto_referencia': 'No centro histórico, próximo ao Mercado Central',
            'como_chegar_transporte': 'Metrô linha 1, estação Central. Ônibus linhas 1101, 1102, 9101',
            'horarios_funcionamento': {
                'segunda': 'Fechado',
                'terca': 'Fechado',
                'quarta': '19:00-02:00',
                'quinta': '19:00-02:00',
                'sexta': '19:00-03:00',
                'sabado': '18:00-03:00',
                'domingo': '18:00-01:00'
            },
            'is_approved': True
        },
        {
            'name': 'Lanchonete do Zé',
            'description': 'Lanches artesanais e sucos naturais desde 1985.',
            'type': 'Lanchonete',
            'cep': '90010-150',
            'state': 'RS',
            'city': 'Porto Alegre',
            'neighborhood': 'Centro Histórico',
            'address': 'Rua dos Andradas, 800',
            'phone': '(51) 3333-7777',
            'is_approved': True
        },
        {
            'name': 'Cafeteria Grão Especial',
            'description': 'Cafés especiais, doces artesanais e ambiente aconchegante.',
            'type': 'Cafeteria',
            'cep': '80010-000',
            'state': 'PR',
            'city': 'Curitiba',
            'neighborhood': 'Centro',
            'address': 'Rua XV de Novembro, 600',
            'phone': '(41) 3333-8888',
            'instagram': '@graoespecial',
            'is_approved': True
        },
        {
            'name': 'Bar da Esquina',
            'description': 'O point do bairro para um happy hour descontraído.',
            'type': 'Bar',
            'cep': '40070-110',
            'state': 'BA',
            'city': 'Salvador',
            'neighborhood': 'Pelourinho',
            'address': 'Largo do Pelourinho, 15',
            'phone': '(71) 3333-9999',
            'whatsapp': '71987654321',
            'is_approved': True
        },
        {
            'name': 'Pizzaria Nonna Rosa',
            'description': 'Pizzas artesanais com massa fermentada naturalmente e ingredientes importados.',
            'type': 'Restaurante',
            'cep': '88010-400',
            'state': 'SC',
            'city': 'Florianópolis',
            'neighborhood': 'Centro',
            'address': 'Rua Felipe Schmidt, 300',
            'phone': '(48) 3333-1111',
            'website': 'https://nonnarosa.com.br',
            'is_approved': True
        },
        {
            'name': 'Boteco do Chico',
            'description': 'Petiscos tradicionais e chopp gelado em ambiente descontraído.',
            'type': 'Bar',
            'cep': '60160-230',
            'state': 'CE',
            'city': 'Fortaleza',
            'neighborhood': 'Aldeota',
            'address': 'Rua Monsenhor Tabosa, 1000',
            'phone': '(85) 3333-2222',
            'instagram': '@botecodochico',
            'is_approved': True
        },
        {
            'name': 'Hamburgueria Artesanal',
            'description': 'Hambúrgueres gourmet com carne angus e pães artesanais.',
            'type': 'Lanchonete',
            'cep': '65020-070',
            'state': 'MA',
            'city': 'São Luís',
            'neighborhood': 'Centro',
            'address': 'Rua do Sol, 200',
            'phone': '(98) 3333-4444',
            'whatsapp': '98976543210',
            'is_approved': True
        },
        {
            'name': 'Bistrô Francês',
            'description': 'Culinária francesa refinada em ambiente elegante e acolhedor.',
            'type': 'Restaurante',
            'cep': '70040-010',
            'state': 'DF',
            'city': 'Brasília',
            'neighborhood': 'Asa Norte',
            'address': 'SQN 202, Bloco A',
            'phone': '(61) 3333-5555',
            'website': 'https://bistrofrances.com.br',
            'is_approved': False  # Este ficará pendente para demonstrar o painel admin
        }
    ]
    
    created_establishments = []
    
    for est_data in establishments_data:
        # Verificar se já existe
        existing = Establishment.query.filter_by(name=est_data['name']).first()
        if existing:
            print(f"✓ Estabelecimento '{est_data['name']}' já existe")
            created_establishments.append(existing)
            continue
        
        establishment = Establishment(
            name=est_data['name'],
            description=est_data['description'],
            type=est_data['type'],
            cep=est_data['cep'],
            state=est_data['state'],
            city=est_data['city'],
            neighborhood=est_data['neighborhood'],
            address=est_data['address'],
            phone=est_data.get('phone'),
            whatsapp=est_data.get('whatsapp'),
            instagram=est_data.get('instagram'),
            website=est_data.get('website'),
            # Novos campos
            faixa_etaria=est_data.get('faixa_etaria', 'Livre'),
            pet_friendly=est_data.get('pet_friendly', False),
            lgbt_friendly=est_data.get('lgbt_friendly', False),
            horarios_funcionamento=est_data.get('horarios_funcionamento', {}),
            delivery=est_data.get('delivery', False),
            link_delivery=est_data.get('link_delivery', ''),
            ponto_referencia=est_data.get('ponto_referencia', ''),
            como_chegar_transporte=est_data.get('como_chegar_transporte', ''),
            is_approved=est_data['is_approved'],
            user_id=establishment_user.id
        )
        
        db.session.add(establishment)
        created_establishments.append(establishment)
        print(f"✓ Estabelecimento '{est_data['name']}' criado")
    
    db.session.commit()
    return created_establishments

def create_establishment_images(establishments):
    """Cria imagens de exemplo para os estabelecimentos."""
    print("Criando imagens dos estabelecimentos...")
    
    # Lista de todas as imagens disponíveis
    image_files = [
        '0H6v5bSGOtpe.jpg',
        '1w3feGTOdQtm.jpg',
        '4gSn5nBzAWSA.jpg',
        '4xp8C9SePQe7.jpg',
        '6nNMK5nFLbTH.jpg',
        '6nqRVEw9RJVL.jpg',
        '8zVhKPYcvZRV.jpg',
        'A1pK0eVXST2M_thumbnail_grid.webp',
        'Aa4UKdJTkSOo.jpg',
        'C4U1EQXjtEF3.jpg',
        'CSavDWDNkmSX.webp',
        'CYs9xWYL8rmF.jpg',
        'CtA78uQ5HaAc.jpg',
        'NVZ2H6hAT2VI_thumbnail_grid.webp',
        'QXM124u6kI5d.jpg',
        'S8Tst19LMrfY.png',
        'SoWANbrtvZIb.jpg',
        'UOZC7xfd0wp4.jpg',
        'VhuTUAfAzkEl.webp',
        'XUx5XCjsXvyu.jpg',
        'fAx9yEBkwduH.jpg',
        'fx1f19fgVlJA.jpg',
        'g5mnZYGrMrW2.jpg',
        'gApEKJ4dC1yE.jpg',
        'i6KrF6Y6b3hM.jpg',
        'iOjPbf1ilDwu.jpg',
        'nAfIgQ5QZdVe.jpg',
        'o7Stjff9Romf.jpg',
        'ptISId0eb5cB.jpg',
        'qqQj03CbzzgJ.jpg',
        'rLeynISoGEAR.png',
        'rb6ifkDqGY0e.jpg',
        'uERydrrG6ZxH.jpg',
        'uhNqTRbUGJT8.jpg',
        'vprH5ufm6iQC.jpg',
        'wNtbmgeqjIJs.jpg',
        'xVNCUuC1Pixd.jpg'
    ]
    
    for i, establishment in enumerate(establishments):
        # Verificar se já tem imagens
        existing_images = EstablishmentImage.query.filter_by(establishment_id=establishment.id).count()
        if existing_images > 0:
            print(f"✓ Estabelecimento '{establishment.name}' já tem imagens")
            continue
        
        # Adicionar 2-4 imagens por estabelecimento
        num_images = random.randint(2, 4)
        selected_images = random.sample(image_files, min(num_images, len(image_files)))
        
        for j, image_file in enumerate(selected_images):
            image = EstablishmentImage(
                establishment_id=establishment.id,
                filename=image_file,
                is_primary=(j == 0)  # Primeira imagem é a principal
            )
            db.session.add(image)
        
        print(f"✓ {num_images} imagens adicionadas para '{establishment.name}'")
    
    db.session.commit()

def create_reviews(establishments):
    """Cria avaliações de exemplo."""
    print("Criando avaliações...")
    
    review_comments = [
        "Excelente atendimento e comida deliciosa!",
        "Ambiente muito agradável, recomendo!",
        "Preços justos e qualidade excepcional.",
        "Voltarei com certeza, adorei a experiência.",
        "Ótimo lugar para ir com a família.",
        "Comida saborosa e ambiente aconchegante.",
        "Atendimento rápido e eficiente.",
        "Uma das melhores experiências gastronômicas da cidade.",
        "Lugar perfeito para um encontro romântico.",
        "Recomendo para quem busca qualidade.",
        "Ambiente descontraído e comida boa.",
        "Preço acessível e sabor incrível.",
        "Staff muito atencioso e prestativo.",
        "Decoração linda e comida maravilhosa.",
        "Vale muito a pena conhecer!"
    ]
    
    reviewer_names = [
        "Maria Silva", "João Santos", "Ana Costa", "Pedro Oliveira",
        "Carla Souza", "Roberto Lima", "Fernanda Alves", "Carlos Pereira",
        "Juliana Rodrigues", "Marcos Ferreira", "Patrícia Martins", "André Barbosa",
        "Luciana Gomes", "Rafael Nascimento", "Camila Ribeiro"
    ]
    
    created_reviews = 0
    
    for establishment in establishments:
        if not establishment.is_approved:
            continue  # Não criar avaliações para estabelecimentos não aprovados
        
        # Criar entre 2 a 8 avaliações por estabelecimento
        num_reviews = random.randint(2, 8)
        
        for _ in range(num_reviews):
            # Verificar se já existe muitas avaliações para este estabelecimento
            existing_reviews = Review.query.filter_by(establishment_id=establishment.id).count()
            if existing_reviews >= 8:
                break
            
            review = Review(
                rating=random.randint(3, 5),  # Avaliações entre 3 e 5 estrelas
                comment=random.choice(review_comments),
                reviewer_name=random.choice(reviewer_names),
                reviewer_email=f"{random.choice(reviewer_names).lower().replace(' ', '.')}@email.com",
                establishment_id=establishment.id,
                is_approved=True
            )
            
            # Definir data de criação aleatória nos últimos 30 dias
            days_ago = random.randint(1, 30)
            review.created_at = datetime.utcnow() - timedelta(days=days_ago)
            
            db.session.add(review)
            created_reviews += 1
    
    db.session.commit()
    print(f"✓ {created_reviews} avaliações criadas")

def main():
    """Função principal."""
    print("🚀 Iniciando população do banco de dados...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Criar usuários
            admin, establishment_user = create_users()
            
            # Criar estabelecimentos
            establishments = create_establishments()
            
            # Criar imagens dos estabelecimentos
            create_establishment_images(establishments)
            
            # Criar avaliações
            create_reviews(establishments)
            
            print("=" * 50)
            print("✅ População do banco de dados concluída com sucesso!")
            print("\n📊 Resumo:")
            print(f"   • Usuários: {User.query.count()}")
            print(f"   • Estabelecimentos: {Establishment.query.count()}")
            print(f"   • Imagens: {EstablishmentImage.query.count()}")
            print(f"   • Avaliações: {Review.query.count()}")
            print("\n🔑 Credenciais de acesso:")
            print("   • Admin: admin@barzinhos.com / 123456")
            print("   • Estabelecimento: bar@exemplo.com / 123456")
            
        except Exception as e:
            print(f"❌ Erro durante a população: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    main()

