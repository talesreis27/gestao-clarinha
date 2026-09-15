
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
