# Intervals Manager 4.0 — Português / English

**Aplicativo independente, gratuito e com código-fonte incluído (Python + Tkinter)** para preparar e organizar treinos do Intervals.icu no Windows. O programa não é oficial nem afiliado ao Intervals.icu.

**Independent, free, source-available Python + Tkinter application** for managing running plans and Intervals.icu workouts on Windows. Not an official Intervals.icu product.

---

## Português (Brasil)

### Instalação
1. Instale o Python 3.10+ pelo site https://python.org/downloads/. Marque **Add Python to PATH**.
2. Extraia o ZIP para uma pasta no Windows (por exemplo, `Documentos\IntervalsManager`).
3. Abra `iniciar_windows.bat` com dois cliques. Ele instala a única dependência (`requests`).
4. Em **Conexão**, informe e salve a API Key do Intervals.icu. Não compartilhe o arquivo `config.json`.
5. Em **Gerador**, o aplicativo carrega o histórico de corrida (se conectado), permite configurar o objetivo e gera uma prévia de treinos.
6. Revise o calendário e os treinos antes de salvá-los. Para publicar, abra o plano em **Meus planos** e clique em **Enviar à API**.

### Idioma
No canto superior direito, escolha **Português (Brasil)** ou **English**. A interface muda imediatamente, sem reiniciar o aplicativo. O idioma é salvo no `config.json` e será reaplicado nas próximas aberturas. Seus campos preenchidos e planos em edição não são descartados.

**Atenção:** planos já publicados ou editados manualmente não são reescritos ao trocar o idioma. Um plano novo é gerado no idioma atualmente selecionado; a prévia de um plano gerado pode ser exibida em ambos os idiomas. Os nomes/observações e o resumo exportado acompanham o idioma escolhido, mas os comandos de treino reconhecidos pelo Intervals.icu continuam os mesmos.

### Funções
- Gerar planos para corrida contínua de 2–10 km ou melhoria de velocidade; 2–5 dias por semana, prazo estimado e data-limite.
- Controlar intensidade por **pace absoluto**, **%FC máxima**, **zona de FC** ou **zona de pace**.
- Analisar atividades de corrida dos últimos 84 dias, avaliando frequência, distância, pace e FC quando disponíveis.
- Criar nomes como `S1-2,4km/25min - Rodagem leve`, com observações breves.
- Salvar planos como `plano.json`, `treinos.csv` e `resumo_para_imprimir.txt` em uma pasta do Windows.
- Abrir/editar planos, publicar via API, consultar calendário, exportar históricos e excluir treinos futuros com confirmação e backup JSON prévio.

**Segurança:** a API Key é salva localmente, em texto simples, no `config.json`. Não compartilhe esse arquivo. Exclusões remotas são permanentes, ainda que o aplicativo crie backups antes de apagar. O backup não é uma restauração automática. As operações em lote não foram validadas na sua conta; experimente primeiro com um treino descartável.

**Limites de treinamento:** distância estimada não é uma meta garantida em treinos por FC/zona; maior distância registrada não significa que a pessoa correu sem caminhar; FC máxima observada não é automaticamente a FCmax verdadeira. As recomendações não substituem orientação profissional.

---

## English

### Installation
1. Install **Python 3.10+** from https://python.org/downloads/ and enable **Add Python to PATH**.
2. Unzip the package to a folder on Windows (for example, `Documents\IntervalsManager`).
3. Double-click `iniciar_windows.bat`. It will install the only dependency (`requests`).
4. Under **Connection**, enter and save your Intervals.icu API key. Do not share `config.json`.
5. Under **Plan Builder**, review your running history (when connected), answer the guided questions and preview your plan.
6. Review all workouts before saving. To upload, open the plan in **My Plans**, then click **Upload to API**.

### Language selection
At the top right, choose **Português (Brasil)** or **English**. All navigation, form labels, dialog buttons/messages, chart labels and plan-builder text can switch without restarting. The choice is saved locally in `config.json` and restored the next time you open the app. Open form data and unsaved workout edits are preserved during switching.

**Note:** Switching language does **not** translate pre-existing or manually edited events in your Intervals.icu account. Newly generated plans use the selected language for workout names (for example `S1-2.4km/25min - Easy run`), short coaching notes and plan guidance. Workout step keywords like `Warmup`, `Z2 HR`, `Pace` and `intensity=active` stay unchanged to preserve API compatibility.

### Features
- Build 2–10 km nonstop-running or speed-improvement plans; choose 2–5 running days/week and a deadline.
- Control workout intensity using **absolute pace**, **% maximum HR**, **HR zones** or **pace zones**.
- Analyze your last 84 days of running activities, including frequency, recorded distance, pace and available HR.
- Generate estimated-distance/total-time workout names and short workout-specific coaching notes.
- Save plans to a Windows folder as `plano.json`, `treinos.csv`, and `resumo_para_imprimir.txt`.
- Open/edit saved plans, upload through the API, back up workouts, export calendar/activity CSVs, or bulk-delete future workouts after confirmation and automatic JSON backup.

**Security:** Your API key is stored locally in plain text in `config.json`; do not share it. Remote deletions are permanent; JSON backups do not automatically restore events. API bulk operations have not been tested in your account. Try a disposable workout first.

**Training limitations:** Estimated kilometers are not exact targets when HR/zones are used. A recorded activity distance does not prove nonstop running. Highest observed HR is not automatically maximum HR. The rule-based generator is not medical or professional coaching advice.

---

## Tests / Testes

Run from the extracted app directory / Rode na pasta do aplicativo:

```powershell
py -m unittest discover -s tests -v
```

Documentation / Documentação: https://intervals.icu/api-docs.html
