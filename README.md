🇺🇸 [English](#-english) | 🇧🇷 [Português](#-português)

---

## 🇺🇸 English

# Class Management System — CT Riozinho

A financial and attendance management system for beach tennis/footvolley instructors, built as a pilot module of a larger management system for CT Riozinho (Florianópolis, Brazil).

🔗 **[Live dashboard](https://gestao-aulas-clarinha.streamlit.app)**

### The problem

Three instructors (Clarinha, Julia, and Maite) taught classes together with no structured control over payments, attendance, or revenue splitting. Everything was tracked from memory, creating risk of errors, missed payments, and no real financial visibility.

### The solution

A complete data pipeline that:
- Captures payments and attendance via Google Forms (simple interface, no app installation needed)
- Automatically processes and validates data with Python/Pandas
- Applies real business rules: monthly fee calculation based on weekly frequency, revenue split per class (respecting which instructors teach which class), late payment detection, and dropout risk alerts
- Displays everything in a real-time visual dashboard

Beyond solving the immediate operational pain point, the project was designed with a long-term goal in mind: **structuring the data cleanly and consistently to enable a future AI layer** — for example, a conversational assistant for querying business data, or automatic anomaly detection (unusual payments, dropout patterns). This attention to data modeling from the start is what makes that evolution possible without rework.

### Tech stack

- **Python** — core language
- **Pandas** — data processing and transformation
- **Streamlit** — interactive dashboard
- **Google Sheets API (gspread)** — data storage and Forms-based capture
- **Google Cloud (Service Account)** — secure authentication
- **Git/GitHub** — version control
- **Streamlit Cloud** — deployment

### Architecture
Google Forms (capture)
↓
Google Sheets (raw data)
↓
Python/Pandas (cleaning + business logic)
↓
Streamlit (dashboard)


The project follows a clear separation between raw and processed data, a common pattern in data engineering pipelines: form responses are never altered directly — all processing happens in isolated code layers (`src/sheets_client.py` for I/O, `src/processamento.py` for business logic), making the system easier to test, maintain, and audit.

### Features

- 💰 **Financial management**: automatic fee calculation based on weekly frequency, payment validation (correct/underpaid/overpaid), pending payment identification
- 🤝 **Automatic revenue split between instructors**: each class has its own set of assigned instructors (e.g. one class split between 2 instructors, another between 3) — the system calculates the correct split with no hardcoded logic
- 📅 **Attendance tracking**: single form with conditional sections per class
- 🏆 **Attendance ranking**: overall and per-class, calculated proportionally to each student's enrolled frequency (avoids skewing results between 1x/week and 2x/week students)
- 🔥 **Attendance streaks**: simple gamification to encourage consistency
- ⚠️ **Automatic alerts**: names found in payments/attendance but not registered, students at dropout risk (2+ weeks absent), automatic inactivation after 4+ weeks of absence
- 📈 **Monthly revenue tracking**: financial evolution over time

### Technical highlights

- **Relational data modeling in spreadsheets**: well-defined entities (`students`, `classes`, `prices`, `payments`, `attendance`) with clear relationships, even without a traditional database
- **Real-world messy data handling**: duplicate names, typos, duplicated headers from Google Forms, Brazilian currency formatting — all handled with dedicated cleaning functions
- **Non-trivial business logic**: proportional payment splitting when a student attends multiple classes; attendance percentage calculated only against the days a student is actually enrolled in (not the class's total sessions)
- **Secure production authentication**: Streamlit Secrets used for sensitive credentials, never exposed in the public repository
- **Custom visual identity**: styled via custom CSS inside Streamlit, matching CT Riozinho's brand

### Running locally

```bash
# Clone the repository
git clone https://github.com/talesreis27/gestao-clarinha.git
cd gestao-clarinha

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up your Google Cloud credentials
# Place your credentials file at credentials/google-credentials.json
# (not included in the repository for security reasons)

# Run the dashboard
streamlit run dashboard/app.py
```

### Future roadmap

- [ ] Replicate the module for other CT Riozinho instructors
- [ ] Unify with the main CT system (court rentals)
- [ ] AI layer: conversational assistant and anomaly detection
- [ ] Referral rewards and class-level goals

### Author

Built by [Tales Reis](https://github.com/talesreis27) as part of a Data Engineering portfolio.

---

## 🇧🇷 Português

# Gestão de Aulas — CT Riozinho

Sistema de gestão financeira e de presença para professoras de aulas de futevôlei/beach tennis, desenvolvido como módulo piloto de um sistema maior de gestão para o CT Riozinho (Florianópolis).

🔗 **[Acesse o dashboard ao vivo](https://gestao-aulas-clarinha.streamlit.app)**

### O problema

Três professoras (Clarinha, Julia e Maite) davam aulas em conjunto sem nenhum controle estruturado de pagamentos, presença ou divisão de receita entre elas. Todo o controle era feito de memória, gerando risco de erro, esquecimento e falta de visibilidade financeira.

### A solução

Um pipeline de dados completo que:
- Captura pagamentos e chamadas via Google Forms (interface simples, sem app a instalar)
- Processa e valida os dados automaticamente com Python/Pandas
- Aplica regras de negócio reais: cálculo de mensalidade por frequência, rateio de receita por turma (respeitando quais professoras dão aula em cada turma), detecção de inadimplência e risco de evasão
- Exibe tudo em um dashboard visual, atualizado em tempo real

Além de resolver a dor operacional imediata, o projeto foi desenhado com um objetivo de longo prazo: **estruturar os dados de forma limpa e consistente para viabilizar, no futuro, uma camada de IA** — por exemplo, um assistente conversacional para consultar informações do negócio, ou detecção automática de anomalias (pagamentos incomuns, padrões de evasão). Esse cuidado com a modelagem de dados desde o início é o que torna essa evolução viável sem retrabalho.

### Stack técnica

- **Python** — linguagem principal
- **Pandas** — processamento e transformação de dados
- **Streamlit** — dashboard interativo
- **Google Sheets API (gspread)** — armazenamento de dados e captura via Forms
- **Google Cloud (Service Account)** — autenticação segura
- **Git/GitHub** — versionamento
- **Streamlit Cloud** — deploy

### Arquitetura

Google Forms (captura)
↓
Google Sheets (dados brutos)
↓
Python/Pandas (limpeza + regras de negócio)
↓
Streamlit (dashboard)


O projeto segue uma separação clara entre dado bruto (`raw`) e dado processado, um padrão comum em pipelines de engenharia de dados: as respostas dos formulários nunca são alteradas diretamente — todo o processamento acontece em camadas de código isoladas (`src/sheets_client.py` para I/O, `src/processamento.py` para lógica de negócio), o que facilita testes, manutenção e auditoria.

### Funcionalidades

- 💰 **Gestão financeira**: cálculo automático de mensalidade por frequência semanal, validação de pagamentos (correto/a menor/a maior), identificação de pendências
- 🤝 **Rateio automático entre professoras**: cada turma tem suas próprias professoras associadas (ex: uma turma pode ser dividida entre 2 professoras, outra entre 3) — o sistema calcula a divisão correta sem hardcode
- 📅 **Controle de presença**: chamada por turma via formulário único com seções condicionais
- 🏆 **Ranking de presença**: geral e por turma, calculado de forma proporcional à frequência contratada de cada aluno (evita distorção entre alunos de 1x/semana e 2x/semana)
- 🔥 **Sequência de presença (streak)**: gamificação simples para incentivar assiduidade
- ⚠️ **Alertas automáticos**: nomes que aparecem em pagamentos/chamadas mas não estão cadastrados, alunos em risco de evasão (2+ semanas sem aparecer), inativação automática após 4+ semanas de ausência
- 📈 **Receita por mês**: acompanhamento da evolução financeira ao longo do tempo

### Destaques técnicos

- **Modelagem de dados relacional em planilhas**: entidades bem definidas (`alunos`, `turmas`, `precos`, `pagamentos`, `presencas`) com relacionamentos claros, mesmo estando em Google Sheets em vez de um banco de dados tradicional
- **Tratamento de dados reais e "sujos"**: nomes duplicados, inconsistências de digitação, cabeçalhos duplicados vindos do Google Forms, valores monetários em formato brasileiro — tudo tratado com funções de limpeza dedicadas
- **Regras de negócio não-triviais**: divisão proporcional de pagamento quando um aluno frequenta múltiplas turmas; cálculo de percentual de presença considerando apenas os dias em que o aluno está matriculado (não o total de aulas da turma)
- **Autenticação segura em produção**: uso de Streamlit Secrets para credenciais sensíveis, nunca expostas no repositório público
- **Interface visual customizada**: identidade visual aplicada via CSS customizado dentro do Streamlit, alinhada à marca do CT Riozinho

### Como rodar localmente

```bash
# Clone o repositório
git clone https://github.com/talesreis27/gestao-clarinha.git
cd gestao-clarinha

# Crie e ative o ambiente virtual
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Configure suas credenciais do Google Cloud
# Coloque o arquivo de credenciais em credentials/google-credentials.json
# (não incluído no repositório por segurança)

# Rode o dashboard
streamlit run dashboard/app.py
```

### Roadmap futuro

- [ ] Replicar o módulo para outros professores do CT Riozinho
- [ ] Unificar com o sistema principal do CT (quadras/locação)
- [ ] Camada de IA: assistente conversacional e detecção de anomalias
- [ ] Sistema de indicação premiada e metas por turma

### Autor

Desenvolvido por [Tales Reis](https://github.com/talesreis27) como parte de um portfólio de projetos em Engenharia de Dados.