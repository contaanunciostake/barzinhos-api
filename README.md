# 🍻 Barzinhos - Plataforma Digital Completa

## 📋 Visão Geral

O **Barzinhos** é uma plataforma digital completa desenvolvida em **React + Flask** que conecta estabelecimentos (bares, restaurantes, pubs) com clientes através de uma vitrine digital moderna e funcional.

### 🎯 Objetivo
Promover bares e restaurantes locais através de uma vitrine digital organizada, com foco em descoberta, avaliações e presença online — sem venda direta de produtos.

## 🚀 Tecnologias Utilizadas

### Frontend
- **React 18** com Vite
- **TailwindCSS** para estilização
- **shadcn/ui** para componentes
- **React Router** para navegação
- **Lucide Icons** para ícones

### Backend
- **Flask** (Python)
- **SQLAlchemy** para ORM
- **Flask-JWT-Extended** para autenticação
- **SQLite** como banco de dados
- **Flask-CORS** para integração frontend-backend

## 🏗️ Arquitetura do Sistema

```
barzinhos_project/
├── frontend/                 # Aplicação React
│   ├── src/
│   │   ├── components/      # Componentes reutilizáveis
│   │   ├── pages/          # Páginas da aplicação
│   │   ├── services/       # Serviços de API
│   │   ├── contexts/       # Contextos React
│   │   └── lib/           # Utilitários
│   └── dist/              # Build de produção
├── backend_flask/           # API Flask
│   ├── src/
│   │   ├── models/        # Modelos de dados
│   │   ├── routes/        # Rotas da API
│   │   └── main.py       # Arquivo principal
│   └── venv/             # Ambiente virtual Python
└── README.md             # Este arquivo
```

## 🔧 Funcionalidades Implementadas

### ✅ Frontend React
- **Página Inicial**: Vitrine pública com busca e filtros
- **Sistema de Autenticação**: Login/logout com JWT
- **Cadastro de Estabelecimentos**: Formulário completo
- **Painel Administrativo**: Aprovação/rejeição de estabelecimentos
- **Painel do Estabelecimento**: Gestão completa do perfil
- **Sistema de Avaliações**: Estrelas e comentários
- **Upload de Imagens**: Logo e galeria de fotos
- **Design Responsivo**: Funciona em desktop e mobile

### ✅ Backend Flask
- **API REST Completa**: Todos os endpoints necessários
- **Autenticação JWT**: Segura e escalável
- **Modelos de Dados**: User, Establishment, Review
- **Sistema de Aprovação**: Workflow completo
- **Upload de Arquivos**: Gestão segura de imagens
- **CORS Configurado**: Integração frontend-backend
- **Banco de Dados**: SQLite com dados de exemplo

### ✅ Funcionalidades de Negócio
- **Busca Inteligente**: Por nome, tipo, bairro
- **Filtros Avançados**: Múltiplos critérios
- **Sistema de Avaliações**: Rating com estrelas
- **Contato Direto**: WhatsApp, telefone, redes sociais
- **Gestão de Status**: Pendente, aprovado, rejeitado
- **Estatísticas**: Dashboard com métricas

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- pnpm

### 1. Backend (Flask)
```bash
cd backend_flask
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```
O backend estará disponível em: `http://localhost:5000`

### 2. Frontend (React)
```bash
cd frontend
pnpm install
pnpm run dev
```
O frontend estará disponível em: `http://localhost:5173`

## 🌐 Endpoints da API

### Autenticação
- `POST /api/auth/login` - Login
- `POST /api/auth/register-establishment` - Cadastro de estabelecimento
- `GET /api/auth/me` - Dados do usuário logado

### Estabelecimentos (Público)
- `GET /api/establishments` - Listar estabelecimentos
- `GET /api/establishments/{id}` - Detalhes do estabelecimento
- `POST /api/establishments` - Criar estabelecimento

### Estabelecimentos (Autenticado)
- `GET /api/establishments/my-establishment` - Meu estabelecimento
- `PUT /api/establishments/my-establishment` - Atualizar meu estabelecimento
- `POST /api/establishments/upload-images` - Upload de imagens

### Administração
- `GET /api/admin/establishments` - Listar todos (admin)
- `PUT /api/admin/establishments/{id}/approve` - Aprovar
- `PUT /api/admin/establishments/{id}/reject` - Rejeitar

### Avaliações
- `GET /api/reviews/establishment/{id}` - Avaliações do estabelecimento
- `POST /api/reviews` - Criar avaliação
- `PUT /api/reviews/{id}` - Atualizar avaliação

## 👥 Tipos de Usuário

### 1. Visitante (Público)
- Visualizar estabelecimentos aprovados
- Buscar e filtrar
- Ver detalhes e avaliações
- Cadastrar novo estabelecimento

### 2. Estabelecimento (Autenticado)
- Gerenciar dados do próprio estabelecimento
- Upload de imagens (logo e galeria)
- Visualizar estatísticas
- Atualizar informações de contato

### 3. Administrador (Autenticado)
- Aprovar/rejeitar estabelecimentos
- Visualizar todos os estabelecimentos
- Dashboard com estatísticas gerais
- Gerenciar sistema completo

## 💰 Modelo de Negócio

### Planos de Assinatura (Futuro)
| Plano | Valor Mensal | Benefícios |
|-------|--------------|------------|
| Bronze | R$ 29 | Ficha básica + mapa + 1 foto |
| Prata | R$ 59 | 5 fotos + destaque + WhatsApp |
| Ouro | R$ 99 | Destaque geral + Stories + Instagram |

### Funcionalidades Premium (Futuro)
- Destaque na busca
- Mais fotos na galeria
- Analytics avançados
- Integração com redes sociais
- Suporte prioritário

## 🔒 Segurança

- **Autenticação JWT**: Tokens seguros com expiração
- **Validação de Dados**: Sanitização de inputs
- **CORS Configurado**: Apenas origens autorizadas
- **Upload Seguro**: Validação de tipos de arquivo
- **Rate Limiting**: Proteção contra spam

## 📱 Responsividade

O sistema foi desenvolvido com **mobile-first**, garantindo:
- Layout adaptável para todas as telas
- Touch-friendly em dispositivos móveis
- Performance otimizada
- Experiência consistente

## 🚀 Deploy

### Frontend (Vercel/Netlify)
```bash
cd frontend
pnpm run build
# Deploy da pasta dist/
```

### Backend (Render/Heroku)
```bash
cd backend_flask
# Configurar variáveis de ambiente
# Deploy do diretório backend_flask/
```

### Variáveis de Ambiente
```env
FLASK_ENV=production
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=sqlite:///app.db
JWT_SECRET_KEY=sua_jwt_secret_aqui
```

## 📊 Dados de Exemplo

O sistema vem com dados pré-populados:
- 5 estabelecimentos de exemplo
- Diferentes tipos (Bar, Restaurante, Pub, etc.)
- Avaliações com estrelas
- Usuários de teste

### Credenciais de Teste
- **Admin**: admin@barzinhos.com / admin123
- **Estabelecimento**: bar@exemplo.com / 123456

## 🔄 Próximos Passos

### Funcionalidades Futuras
- [ ] Sistema de pagamentos (Stripe/MercadoPago)
- [ ] Notificações push
- [ ] App mobile nativo
- [ ] Integração com Google Maps
- [ ] Sistema de eventos
- [ ] Chat em tempo real
- [ ] Analytics avançados
- [ ] Multi-idiomas

### Melhorias Técnicas
- [ ] Migração para PostgreSQL
- [ ] Cache com Redis
- [ ] CDN para imagens
- [ ] Testes automatizados
- [ ] CI/CD pipeline
- [ ] Monitoramento
- [ ] Backup automático

## 📞 Suporte

Para dúvidas ou suporte:
- **Email**: suporte@barzinhos.com
- **WhatsApp**: (21) 99999-9999
- **Site**: https://barzinhos.com.br

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido com ❤️ pela equipe Barzinhos**

*Conectando estabelecimentos a clientes através da tecnologia*

