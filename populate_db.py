#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models.user import db
from src.models.establishment import Establishment, Review

def populate_database():
    """Popular o banco de dados com dados de exemplo"""
    with app.app_context():
        # Limpar dados existentes
        db.drop_all()
        db.create_all()
        
        # Estabelecimentos de exemplo
        establishments = [
            {
                'name': 'Boteco do João',
                'description': 'Ambiente aconchegante com os melhores petiscos da região',
                'address': 'Rua dos Pinheiros, 123',
                'neighborhood': 'Vila Madalena',
                'phone': '(11) 99999-9999',
                'whatsapp': '5511999999999',
                'type': 'Boteco',
                'is_open': True,
                'latitude': -23.5505,
                'longitude': -46.6333,
                'image_url': '/src/assets/restaurant-1.jpg',
                'plan_type': 'ouro',
                'is_approved': True
            },
            {
                'name': 'Choperia Central',
                'description': 'Chopp gelado e ambiente descontraído no coração da cidade',
                'address': 'Av. Paulista, 456',
                'neighborhood': 'Centro',
                'phone': '(11) 88888-8888',
                'whatsapp': '5511888888888',
                'type': 'Choperia',
                'is_open': False,
                'latitude': -23.5618,
                'longitude': -46.6565,
                'image_url': '/src/assets/restaurant-2.jpg',
                'plan_type': 'prata',
                'is_approved': True
            },
            {
                'name': 'Petiscaria da Esquina',
                'description': 'Os melhores petiscos tradicionais em um ambiente familiar',
                'address': 'Rua da Consolação, 789',
                'neighborhood': 'Pinheiros',
                'phone': '(11) 77777-7777',
                'whatsapp': '5511777777777',
                'type': 'Petiscaria',
                'is_open': True,
                'latitude': -23.5489,
                'longitude': -46.6388,
                'image_url': '/src/assets/restaurant-3.jpg',
                'plan_type': 'bronze',
                'is_approved': True
            },
            {
                'name': 'Bar do Zé',
                'description': 'Tradicional bar de bairro com música ao vivo',
                'address': 'Rua Augusta, 321',
                'neighborhood': 'Itaim',
                'phone': '(11) 66666-6666',
                'whatsapp': '5511666666666',
                'type': 'Bar',
                'is_open': True,
                'latitude': -23.5729,
                'longitude': -46.6520,
                'image_url': '/src/assets/restaurant-4.jpg',
                'plan_type': 'bronze',
                'is_approved': True
            },
            {
                'name': 'Restaurante Sabor Mineiro',
                'description': 'Comida mineira autêntica em ambiente acolhedor',
                'address': 'Rua dos Três Irmãos, 654',
                'neighborhood': 'Moema',
                'phone': '(11) 55555-5555',
                'whatsapp': '5511555555555',
                'type': 'Restaurante',
                'is_open': True,
                'latitude': -23.6024,
                'longitude': -46.6734,
                'image_url': '/src/assets/restaurant-5.jpg',
                'plan_type': 'prata',
                'is_approved': True
            },
            {
                'name': 'Pizzaria Napolitana',
                'description': 'As melhores pizzas artesanais da cidade, forno a lenha.',
                'address': 'Rua da Paz, 100',
                'neighborhood': 'Brooklin',
                'phone': '(11) 44444-4444',
                'whatsapp': '5511444444444',
                'type': 'Pizzaria',
                'is_open': True,
                'latitude': -23.6181,
                'longitude': -46.6978,
                'image_url': '/src/assets/restaurant-6.jpg',
                'plan_type': 'ouro',
                'is_approved': True
            },
            {
                'name': 'Café Literário',
                'description': 'Um espaço tranquilo para ler e saborear cafés especiais.',
                'address': 'Praça da Árvore, 50',
                'neighborhood': 'Vila Mariana',
                'phone': '(11) 33333-3333',
                'whatsapp': '5511333333333',
                'type': 'Cafeteria',
                'is_open': True,
                'latitude': -23.5999,
                'longitude': -46.6388,
                'image_url': '/src/assets/restaurant-7.jpg',
                'plan_type': 'bronze',
                'is_approved': True
            },
            {
                'name': 'Hamburgueria Artesanal',
                'description': 'Hambúrgueres gourmet com ingredientes frescos e selecionados.',
                'address': 'Av. Brasil, 2000',
                'neighborhood': 'Jardins',
                'phone': '(11) 22222-2222',
                'whatsapp': '5511222222222',
                'type': 'Hamburgueria',
                'is_open': True,
                'latitude': -23.5613,
                'longitude': -46.6611,
                'image_url': '/src/assets/restaurant-8.jpg',
                'plan_type': 'prata',
                'is_approved': True
            }
        ]
        
        # Criar estabelecimentos
        created_establishments = []
        for est_data in establishments:
            establishment = Establishment(**est_data)
            db.session.add(establishment)
            created_establishments.append(establishment)
        
        db.session.commit()
        
        # Adicionar avaliações de exemplo
        reviews = [
            {'establishment_id': 1, 'user_name': 'Maria Silva', 'rating': 5, 'comment': 'Excelente ambiente e petiscos deliciosos!'},
            {'establishment_id': 1, 'user_name': 'João Santos', 'rating': 4, 'comment': 'Muito bom, recomendo!'},
            {'establishment_id': 2, 'user_name': 'Ana Costa', 'rating': 4, 'comment': 'Chopp gelado e bom atendimento.'},
            {'establishment_id': 2, 'user_name': 'Pedro Lima', 'rating': 4, 'comment': 'Local agradável para happy hour.'},
            {'establishment_id': 3, 'user_name': 'Carlos Oliveira', 'rating': 5, 'comment': 'Melhor petiscaria da região!'},
            {'establishment_id': 3, 'user_name': 'Lucia Ferreira', 'rating': 5, 'comment': 'Ambiente familiar e comida excelente.'},
            {'establishment_id': 3, 'user_name': 'Roberto Alves', 'rating': 4, 'comment': 'Muito bom, voltarei sempre.'},
            {'establishment_id': 4, 'user_name': 'Fernanda Rocha', 'rating': 4, 'comment': 'Música ao vivo é ótima!'},
            {'establishment_id': 5, 'user_name': 'Marcos Pereira', 'rating': 5, 'comment': 'Comida mineira autêntica, adorei!'},
            {'establishment_id': 6, 'user_name': 'Mariana Souza', 'rating': 5, 'comment': 'Pizza maravilhosa, massa perfeita!'},
            {'establishment_id': 6, 'user_name': 'Ricardo Gomes', 'rating': 4, 'comment': 'Ótimo lugar para ir com a família.'},
            {'establishment_id': 7, 'user_name': 'Patrícia Lima', 'rating': 5, 'comment': 'Café delicioso e ambiente super acolhedor.'},
            {'establishment_id': 8, 'user_name': 'Bruno Costa', 'rating': 4, 'comment': 'Hambúrguer suculento e batata crocante.'}
        ]
        
        for review_data in reviews:
            review = Review(**review_data)
            db.session.add(review)
        
        db.session.commit()
        
        print(f"Banco de dados populado com {len(establishments)} estabelecimentos e {len(reviews)} avaliações!")

if __name__ == '__main__':
    populate_database()



