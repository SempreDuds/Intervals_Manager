# 🏃‍♂️ Intervals Manager

> **Estúdio local de gestão, análise e geração de planos de treino de corrida integrados ao [Intervals.icu](https://intervals.icu/).**

O **Intervals Manager** é uma aplicação desktop leve e offline-first desenvolvida em Python/Tkinter. Ele permite analisar seu histórico de atividades, gerar planos de treino personalizados e estruturados para corrida, e sincronizar seu calendário diretamente com o Intervals.icu de forma segura e transparente.

---

## 🌟 Principais Funcionalidades

### 📊 1. Análise Cautelosa de Atividades
- Conecta-se à API do Intervals.icu para analisar seu histórico de corridas dos últimos 84 dias (12 semanas).
- Consolida métricas como volume semanal (km), frequência, pace mediano e frequência cardíaca média.
- **Abordagem segura:** Não presume que distâncias totais foram registradas sem caminhada e não converte picos de FC observados em FC máxima fisiológica.

### 🎯 2. Gerador Inteligente de Planos de Corrida
- Entrevista interativa baseada nos seus objetivos (*ex.: correr 5 km sem parar ou melhorar ritmo*).
- Prescreve treinos estruturados (aquecimento, blocos/séries, regenerativos e desaquecimento).
- Suporta múltiplos métodos de controle: **Pace absoluto**, **FC (%FCmax)**, **Zonas de FC** e **Zonas de Pace**.
- Inclui alertas automáticos sobre prazos incompatíveis, dias consecutivos sem descanso e histórico insuficiente.

### 📝 3. Editor Local & Sincronização
- Crie, edite e organize seus planos localmente em formato **JSON** ou **CSV**.
- Sincronize novos treinos com sua conta no Intervals.icu com detecção prévia de duplicatas antes do envio.

### 📅 4. Gestão de Calendário & Backup Seguro
- Visualize e filtre treinos futuros diretamente pela aplicação.
- **Backup automático obrigatório:** Realiza backup em JSON antes de qualquer exclusão em massa.
- Proteção de dados: Apaga apenas eventos planejados (*WORKOUT*), preservando todas as suas atividades já executadas.

### 🔒 5. Privacidade & Segurança
- **100% Local:** Sua chave de API fica salva exclusivamente no seu computador (`config.json`).
- Sem dependência de servidores de terceiros ou serviços de IA em nuvem.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Interface Gráfica:** Tkinter (ttk)
- **Integração:** Requests (API REST Intervals.icu)

---

## 🚀 Como Executar

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
   cd seu-repositorio
