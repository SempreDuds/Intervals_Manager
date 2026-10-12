"""Bilingual UI strings (Português brasileiro / English).

Portuguese text is the stable message ID for compatibility with v3. A language
change only modifies display strings; API types/codes remain unchanged.
"""
import re

LANGUAGES = {'pt_BR': 'Português (Brasil)', 'en': 'English'}
_CURRENT = 'pt_BR'

# Keep translations here; add new keys rather than translating arbitrary user data.
EN = {
    # Main window
    'Intervals Manager 4.0 | Seu estúdio de corrida': 'Intervals Manager 4.0 | Your running studio',
    'Treino inteligente, no seu ritmo': 'Smarter training, at your pace',
    'v4.0  •  WINDOWS + PYTHON': 'v4.0  •  WINDOWS + PYTHON',
    '  Gerador  ': '  Plan Builder  ',
    '  Calendário  ': '  Calendar  ',
    '  Meus planos  ': '  My Plans  ',
    '  Exportações  ': '  Exports  ',
    '  Conexão  ': '  Connection  ',
    'Pronto. Configure a API Key na primeira aba.': 'Ready. Configure your API key in the Connection tab.',
    'Concluído.': 'Done.',
    'Conectar ao Intervals.icu': 'Connect to Intervals.icu',
    'Sua API Key fica armazenada apenas neste computador, no arquivo config.json. Não compartilhe este arquivo.': 'Your API key is stored locally in config.json. Do not share this file.',
    'API Key (Intervals.icu → Settings → API key)': 'API key (Intervals.icu → Settings → API key)',
    'Idioma': 'Language',
    'Salvar chave': 'Save key',
    'Testar conexão': 'Test connection',
    'Importante: para excluir eventos, a sua chave precisa ter permissão de acesso ao calendário.': 'Important: your API key needs calendar access to delete workouts.',
    'Abrir site do Intervals.icu': 'Open Intervals.icu website',
    'Configuração': 'Settings',
    'Chave salva localmente. Guarde o arquivo config.json em segurança.': 'API key saved locally. Keep config.json secure.',
    'Testando conexão...': 'Testing connection...',
    'Conexão funcionando!': 'Connection successful!',
    'Conexão': 'Connection',
    'Calendário e exclusão em massa': 'Calendar and bulk deletion',
    'De:': 'From:', 'Até:': 'To:', 'Consultar': 'Refresh',
    'Apenas treinos de hoje em diante': 'Only workouts from today onward',
    'Data': 'Date', 'Modalidade': 'Sport', 'Treino': 'Workout', 'ID': 'ID',
    'Backup dos treinos exibidos': 'Back up displayed workouts',
    'Excluir selecionados': 'Delete selected',
    'EXCLUIR TODOS OS FUTUROS': 'DELETE ALL FUTURE WORKOUTS',
    'A exclusão só atinge eventos WORKOUT do calendário; atividades realizadas não são apagadas. Backup é obrigatório antes da exclusão.': 'Deletion only affects planned WORKOUT events. Completed activities are not deleted. A backup is required first.',
    'Data inicial posterior à final.': 'Start date is after end date.',
    'Limite de consulta: 10 anos.': 'Maximum query range: 10 years.',
    'Consultando calendário...': 'Loading calendar...',
    'Não há treinos exibidos. Consulte o calendário.': 'No workouts shown. Refresh the calendar first.',
    'Backup': 'Backup',
    'Nenhum treino planejado elegível para exclusão.': 'No eligible planned workouts to delete.',
    'Sem treinos': 'No workouts',
    'Confirmar EXCLUSÃO': 'Confirm DELETION',
    'Buscando treinos futuros até 2100...': 'Finding future workouts through 2100...',
    'Excluindo treinos com backup...': 'Backing up and deleting workouts...',
    'Resultado parcial': 'Partial result', 'Resultado': 'Result',
    'Planos locais: editar, salvar e importar': 'Local plans: edit, save and upload',
    'Novo plano': 'New plan', 'Abrir JSON/CSV': 'Open JSON/CSV',
    'Salvar JSON': 'Save JSON', 'Enviar à API': 'Upload to API',
    'Plano não aberto': 'No plan open',
    'Adicionar treino': 'Add workout', 'Remover': 'Remove',
    'Data (AAAA-MM-DD)': 'Date (YYYY-MM-DD)', 'Título': 'Title',
    'Descrição do treino (linguagem nativa do Intervals.icu)': 'Workout description (Intervals.icu syntax)',
    'Aplicar alterações neste treino': 'Apply changes to this workout',
    'Dica: inclua uma data diferente em cada treino. Ao enviar, o aplicativo cria eventos novos; não substitui treinos existentes.': 'Tip: use a different date for each workout. Uploading creates new events and does not replace existing workouts.',
    'Descartar plano ainda aberto? Salve primeiro se necessário.': 'Discard the currently open plan? Save it first if needed.',
    'Datas': 'Dates',
    'Planos JSON/CSV': 'JSON/CSV plans', 'Plano JSON': 'JSON plan',
    'Treino sem data: use start_date_local, date ou data.': 'Workout has no date: use start_date_local, date or data.',
    'Abrir plano': 'Open plan', 'Salvar plano': 'Save plan',
    'Salvar': 'Save',
    'Adicione pelo menos um treino.': 'Add at least one workout.',
    'Salvo': 'Saved', 'Plano novo (ainda não salvo)': 'New plan (not saved)',
    'Novo treino': 'New workout',
    'Editar': 'Edit', 'Selecione um treino.': 'Select a workout.',
    'Use uma data válida: AAAA-MM-DD': 'Enter a valid date: YYYY-MM-DD',
    'Treino atualizado na memória. Clique em Salvar JSON para gravar no disco.': 'Workout updated in memory. Click Save JSON to write it to disk.',
    'Abrir no editor': 'Open in editor',
    'O editor contém outro plano. Salve-o antes de substituir. Continuar?': 'Another plan is open in the editor. Save it before replacing it. Continue?',
    'Plano do gerador carregado no editor. Revise, salve e só então envie à API.': 'Generated plan loaded in the editor. Review and save it before uploading.',
    'Importação': 'Import', 'Abra ou crie um plano primeiro.': 'Open or create a plan first.',
    'O plano contém datas e títulos duplicados. Revise primeiro.': 'This plan has duplicate dates and titles. Review it first.',
    'Plano inválido': 'Invalid plan', 'Enviar plano': 'Upload plan',
    'Duplicatas detectadas': 'Duplicates found',
    'Conferindo possíveis duplicatas...': 'Checking for possible duplicates...',
    'Enviando treinos para o Intervals.icu...': 'Uploading workouts to Intervals.icu...',
    'Data inicial posterior à final.': 'Start date is after end date.',
    'Envio solicitado': 'Upload submitted',
    'Ferramentas de exportação': 'Export tools',
    'As datas da consulta são as mesmas definidas na aba Calendário.': 'The export uses the date range selected in the Calendar tab.',
    'Exportar calendário completo (JSON)': 'Export full calendar (JSON)',
    'Exportar treinos planejados (CSV)': 'Export planned workouts (CSV)',
    'Exportar atividades realizadas (CSV)': 'Export completed activities (CSV)',
    'Abrir pasta de planos': 'Open plans folder', 'Abrir pasta de backups': 'Open backups folder',
    'Os backups JSON preservam dados do calendário, inclusive campos extras, para consulta. Ao abrir um backup como plano, apenas os campos essenciais são importados.': 'JSON backups retain calendar data, including extra fields. When opened as plans, only essential workout fields are imported.',
    'Exportação': 'Export', 'Exportando calendário...': 'Exporting calendar...',
    'Exportando treinos...': 'Exporting workouts...',
    'Exportando atividades...': 'Exporting activities...',
    'Atividades': 'Activities',
    'Informe sua API Key em Configuração.': 'Enter your API key in Connection.',
    'O Intervals.icu não retornou uma lista de atividades válida.': 'Intervals.icu did not return a valid activity list.',
    'Erro': 'Error', 'Falha de rede: ': 'Network error: ',
    # Plan assistant
    'Entrevista — Gerador de plano de corrida': 'Running plan builder — Questionnaire',
    'Meu plano 5 km': 'My 5K plan',
    'Responda às perguntas para personalizar sua programação': 'Answer a few questions to personalize your plan',
    'Os valores abaixo são só exemplos. Altere conforme seu nível real; o gerador funciona offline.': 'These are example values. Change them to match your current level; the builder works offline.',
    'Dados reais carregados • confira a maior distância SEM caminhar': 'Activity history loaded • confirm your longest NONSTOP running distance',
    '1. Objetivo e nível': '1. Goal & fitness',
    '2. Dias e prazo': '2. Schedule & deadline',
    '3. Intensidade e cuidados': '3. Intensity & safety',
    'Nome do plano': 'Plan name',
    'Ex.: 5 km sem parar — Primavera': 'E.g. Nonstop 5K — Spring',
    'Principal objetivo': 'Main goal',
    'Correr sem parar': 'Run nonstop', 'Melhorar velocidade': 'Improve speed',
    'Distância alvo (km)': 'Target distance (km)',
    'Ex.: 3, 4, 5, 10. Aceita vírgula.': 'E.g. 3, 4, 5, 10. Decimal comma or point works.',
    'Maior distância sem caminhar (km)': 'Longest distance without walking (km)',
    'Use 0 se ainda não corre continuamente.': 'Use 0 if you cannot yet run continuously.',
    'Informar ritmos como': 'Enter running speed as',
    'Pace (min/km)': 'Pace (min/km)', 'Velocidade (km/h)': 'Speed (km/h)',
    'Pace atual (min/km)': 'Current pace (min/km)',
    'Pace objetivo (min/km)': 'Target pace (min/km)',
    'Velocidade atual (km/h)': 'Current speed (km/h)',
    'Velocidade objetivo (km/h)': 'Target speed (km/h)',
    'Ex.: 08:00 min/km ou 7,5 km/h': 'E.g. 08:00 min/km or 7.5 km/h',
    'Histórico recente de corrida': 'Recent running experience',
    'Iniciante / parado': 'Beginner / inactive',
    'Regular (1-3 meses)': 'Regular (1–3 months)',
    'Regular (>3 meses)': 'Regular (>3 months)',
    'Exemplo: ritmo atual de 08:00 min/km significa 7,5 km/h. Para ficar mais rápido, o pace alvo deve ser MENOR.': 'Example: 08:00 min/km means 7.5 km/h. A faster target pace must have a SMALLER number.',
    'Quantos treinos por semana?': 'How many runs per week?',
    'Quais dias você PODE correr? (marque pelo menos a quantidade indicada)': 'Which days CAN you run? (select at least the number above)',
    'Seg': 'Mon', 'Ter': 'Tue', 'Qua': 'Wed', 'Qui': 'Thu', 'Sex': 'Fri', 'Sab': 'Sat', 'Dom': 'Sun',
    'Data mínima para começar': 'Earliest start date',
    'Data-limite desejada': 'Desired deadline',
    'AAAA-MM-DD': 'YYYY-MM-DD',
    'AAAA-MM-DD (pode deixar vazio)': 'YYYY-MM-DD (optional)',
    'O sistema escolhe os dias mais espaçados e sugere um prazo. Se a data-limite for muito cedo, ele avisa e preserva a progressão em vez de acelerar o plano.': 'The builder spaces runs apart and recommends a timeframe. If the deadline is too soon, it warns you rather than rushing progression.',
    'Como controlar os treinos?': 'How should workout intensity be prescribed?',
    'Pace absoluto': 'Absolute pace', 'FC (%FCmax)': 'HR (%HRmax)',
    'Zona de FC': 'Heart rate zone', 'Zona de pace': 'Pace zone',
    'FC máxima (bpm)': 'Maximum HR (bpm)',
    'Tive lesão ou desconforto recente que pode limitar os treinos': 'Recent injury or discomfort that might limit training',
    'O gerador é educativo e conservador; não faz diagnóstico. Em caso de sintomas ou retorno pós-lesão, procure avaliação profissional antes de seguir o plano.': 'This educational plan builder does not diagnose medical conditions. Consult a professional if you have symptoms or are returning from injury.',
    'Cancelar': 'Cancel', 'Gerar plano e visualizar  →': 'Generate plan and preview  →',
    'Usa faixas como 65-74% HR. Informe FCmax confiável; não converte bpm exato em etapas, pois a API do Intervals usa % ou zonas.': 'Uses ranges such as 65-74% HR. Enter a reliable HRmax; Intervals uses percentages or zones, not exact BPM steps here.',
    'Usa faixas absolutas como 08:40-08:20/km Pace; não depende do pace limiar salvo no Intervals.icu.': 'Uses absolute pace ranges such as 08:40-08:20/km Pace; not dependent on the threshold pace saved in Intervals.icu.',
    'Usa Z1 HR, Z2 HR e Z3 HR. Configure e revise suas zonas de FC de corrida no Intervals.icu.': 'Uses Z1 HR, Z2 HR and Z3 HR. Configure and review your running HR zones in Intervals.icu.',
    'Usa Z1 Pace, Z2 Pace e Z3 Pace. Configure e revise suas zonas de pace de corrida no Intervals.icu.': 'Uses Z1 Pace, Z2 Pace and Z3 Pace. Configure and review your pace zones in Intervals.icu.',
    'Velocidade precisa ficar entre 3 e 20 km/h.': 'Speed must be between 3 and 20 km/h.',
    'Verifique as respostas': 'Check your answers',
    'Planeje sua próxima conquista': 'Plan your next milestone',
    'O sistema faz perguntas, sugere a duração e monta treinos estruturados para revisar antes de publicar.': 'Answer guided questions to get a suggested timeframe and structured workouts to review before uploading.',
    'Ler minhas corridas': 'Analyze my runs',
    'Criar plano': 'Create plan',
    '2. Salvar plano no Windows': '2. Save plan to Windows',
    '3. Abrir no editor': '3. Open in editor',
    'Sem análise carregada. Clique em “Ler minhas corridas” para personalizar o gerador.': 'No analysis loaded. Click “Analyze my runs” to personalize your plan.',
    'Nenhum plano gerado. Clique em “Criar plano” para começar.': 'No plan generated yet. Click “Create plan” to begin.',
    'Data': 'Date', 'Semana': 'Week', 'Etapa': 'Phase', 'Min. aprox.': 'Approx. min',
    'Treino selecionado / Observações': 'Selected workout / Notes',
    'Não envia automaticamente. Depois de conferir, salve, abra no editor e use “Enviar à API” na aba Planos locais.': 'Workouts are NOT uploaded automatically. Review, save, open in the editor, then select “Upload to API” in My Plans.',
    'VOLUME SEMANAL  •  ÚLTIMAS 8 SEMANAS': 'WEEKLY DISTANCE  •  LAST 8 WEEKS',
    'Conecte sua conta para visualizar o histórico de corrida.': 'Connect your account to see your running history.',
    'API Key necessária': 'API key required',
    'Vá em Conexão, informe sua API Key e depois volte ao Gerador.': 'Go to Connection, enter your API key, then return to Plan Builder.',
    'Analisando suas corridas no Intervals.icu...': 'Analyzing your runs on Intervals.icu...',
    'HISTÓRICO REAL  •  ': 'ACTIVITY HISTORY  •  ',
    'Histórico limitado': 'Limited activity history',
    'Poucas corridas recentes para personalização segura. O sistema seguirá conservador.\n\n': 'Too few recent runs for reliable personalization. The plan will remain conservative.\n\n',
    'ORIENTAÇÕES GERAIS DO PLANO (não repetidas em cada treino)\n\n': 'GENERAL PLAN GUIDANCE (not repeated in every workout)\n\n',
    'OBSERVAÇÃO DO TREINO\n': 'WORKOUT NOTE\n',
    '\n\nESTRUTURA PARA O INTERVALS.ICU\n\n': '\n\nSTRUCTURED STEPS FOR INTERVALS.ICU\n\n',
    'Em FC e zonas, o valor é uma projeção, não uma meta exata.': 'For HR and zone workouts, distance is an estimate, not an exact target.',
    'Plano calculado localmente. Revise e salve antes de enviar.': 'Plan generated locally. Review and save before uploading.',
    'Gerador': 'Plan Builder', 'Gere um plano primeiro.': 'Generate a plan first.',
    'Escolha onde salvar a pasta do plano': 'Choose where to save the plan folder',
    'Plano salvo': 'Plan saved',
    'Pasta criada:': 'Folder created:',
    'Escolha onde salvar a pasta do plano': 'Choose a folder for your training plan',
    'Arquivos: plano.json, treinos.csv, resumo_para_imprimir.txt': 'Files: plano.json, treinos.csv, resumo_para_imprimir.txt',
    'Plano salvo em: ': 'Plan saved to: ',
    'Plano salvo em:': 'Plan saved to:',
    'PLANO: ': 'PLAN: ', 'Duração estimada: ': 'Estimated duration: ',
    ' semanas': ' weeks', 'Período: ': 'Period: ',
    ' até ': ' to ', 'Dias: ': 'Days: ',
    'ORIENTAÇÕES\n': 'GUIDANCE\n', 'TREINOS\n\n': 'WORKOUTS\n\n',
    # Workout names / notes / phases — preserve Intervals.icu step syntax
    'Rodagem leve': 'Easy run', 'Longão': 'Long run',
    'Regenerativo': 'Recovery run', 'Corrida/caminhada': 'Run/walk',
    'Fartlek': 'Fartlek', 'Intervalado': 'Intervals', 'Teste': 'Time trial',
    'Adaptação': 'Base building', 'Construção': 'Build',
    'Consolidação': 'Consolidation', 'Objetivo': 'Goal',
    'Corrida leve': 'Easy run', 'Corrida fácil': 'Easy running',
    'Corrida / caminhada': 'Run / walk',
    'Corrida contínua principal': 'Main continuous run',
    'Teste de distância contínua': 'Nonstop distance test',
    'Teste de pace': 'Pace test',
    'Rodagem de resistência': 'Endurance run',
    'Blocos controlados': 'Controlled intervals', 'Fartlek controlado': 'Controlled fartlek',
    'Intervalos fáceis': 'Easy run/walk intervals',
    'Dica: ': 'Tip: ',
    'Corra em ritmo confortável, conseguindo conversar. Priorize terminar bem.': 'Run at a comfortable, conversational effort. Finish feeling strong.',
    'Alterne trechos vivos e leves sem sprintar; recupere o fôlego.': 'Alternate quicker and easier efforts without sprinting; recover your breath.',
    'Faça os blocos com controle. Desacelere se não recuperar bem.': 'Keep intervals controlled. Slow down if recovery feels insufficient.',
    'Comece conservador e tente manter um ritmo estável até o fim.': 'Start conservatively and aim to maintain a steady effort to the finish.',
    'Intercale corrida leve e caminhada; mantenha a respiração confortável.': 'Alternate easy running and walking; keep breathing comfortable.',
    'Rode bem leve. Hoje o foco é recuperar, não ganhar velocidade.': 'Keep it very easy. Focus on recovery, not speed.',
    'Rode leve e solto, em ritmo de conversa; hidrate-se e recupere bem.': 'Run relaxed at conversational pace; hydrate and recover.',
    # Engine validation & guidance
    'Digite pace no formato MM:SS, por exemplo 08:00.': 'Enter pace as MM:SS, for example 08:00.',
    'Informe um pace plausível entre 03:00 e 20:00 min/km.': 'Enter a plausible pace between 03:00 and 20:00 min/km.',
    'O nome deve ter entre 2 e 90 caracteres.': 'The plan name must be 2–90 characters long.',
    'Selecione um objetivo e método de intensidade válidos.': 'Select a valid goal and intensity method.',
    'A distância objetivo precisa ficar entre 2 e 10 km.': 'Target distance must be between 2 and 10 km.',
    'Informe uma distância atual válida (0 a 100 km).': 'Enter a valid current distance (0–100 km).',
    'Escolha entre 2 e 5 treinos por semana.': 'Select 2–5 runs per week.',
    'Marque pelo menos tantos dias disponíveis quanto os treinos semanais.': 'Select at least as many available days as weekly runs.',
    'Dias da semana inválidos.': 'Invalid weekdays.',
    'Para FC, informe FC máxima medida ou estimada conscientemente, entre 100 e 230 bpm.': 'For HR, enter a reliably measured/estimated maximum HR between 100 and 230 bpm.',
    'A data inicial não pode estar no passado.': 'Start date cannot be in the past.',
    'A data limite não pode ser anterior ao início.': 'Deadline cannot be earlier than start date.',
    'Para ganhar velocidade, o pace objetivo deve ser MENOR que o atual (ex.: 07:30 é mais rápido que 08:00).': 'To improve speed, target pace must be LOWER than your current pace (e.g. 07:30 is faster than 08:00).',
    'Plano estimado por regras conservadoras; não garante desempenho nem substitui avaliação de treinador.': 'Rule-based conservative plan. It does not guarantee performance or replace a qualified coach.',
    'Inclui aquecimento e desaquecimento; intensidade leve significa conseguir conversar.': 'Includes warmups and cooldowns; easy intensity should allow conversation.',
    'Se não concluir uma semana com conforto, repita-a antes de progredir. Dor persistente: interrompa o treino e busque avaliação.': 'Repeat a week if you cannot finish it comfortably. Stop and seek advice for persistent pain.',
    'Verifique as zonas da modalidade Run no Intervals.icu; Z1/Z2/Z3 dependem do perfil e não são calculadas aqui.': 'Verify your running Z1/Z2/Z3 zones in Intervals.icu; zone values depend on your profile.',
    'Paces são estimativas baseadas no pace informado, não um teste de limiar. Em calor/subidas, priorize esforço confortável.': 'Paces are estimates based on the pace you entered, not a threshold test. In heat or hills, prioritize comfortable effort.',
    'Como foi assinalado desconforto/lesão recente, o plano evita sessões intensas e adiciona semanas. Procure orientação antes de retomar se houver sintomas.': 'Recent discomfort/injury was reported, so the plan avoids intense sessions and adds weeks. Seek advice before resuming if symptomatic.',
    'Quatro ou cinco sessões podem ser demais para alguns iniciantes. Considere começar com 3 sessões e manter dias extras opcionais.': 'Four or five sessions may be too much for beginners. Consider three sessions and keep extra days optional.',
    'Há sessões em dias consecutivos devido à disponibilidade. Mantenha-as fáceis; tente separar corridas por um dia de descanso.': 'Your schedule includes back-to-back days. Keep them easy and aim for rest between runs when possible.',
    'Poucas corridas recentes: mantenha informações manuais e interprete o prazo com cautela.': 'Few recent runs: rely on your manual inputs and treat the timeframe cautiously.',
    'Sua corrida contínua atual é menor que a distância-alvo. O plano prioriza adaptação antes dos blocos rápidos.': 'Your nonstop distance is below your target, so the plan prioritizes adaptation before faster intervals.',
    'Volume recente muito baixo: as primeiras sessões devem ser feitas com pausas de caminhada; dias extras podem ser opcionais.': 'Very low recent volume: use walking breaks early on; additional running days may remain optional.',
    # Activity summaries and warnings
    'Nenhuma corrida válida encontrada nos últimos 84 dias. Informe seu nível manualmente.': 'No valid runs found in the last 84 days. Enter your level manually.',
    'Histórico insuficiente (menos de 4 corridas em 8 semanas): recomendações pouco confiáveis.': 'Limited history (fewer than 4 runs in 8 weeks): recommendations have low confidence.',
    'Sem FC média válida no período. Nenhuma meta de FC será inferida.': 'No valid average HR in this period. HR targets will not be inferred.',
    'Distância registrada não prova corrida sem caminhar. Confirme sua maior distância contínua no formulário.': 'Total activity distance does not prove nonstop running. Confirm your longest nonstop distance manually.',
    'FC máxima registrada em um treino NÃO é sua FCmax real; não será usada como FCmax automaticamente.': 'Highest recorded HR is NOT automatically your true HRmax and will not be used as such.',
    'indisponível': 'unavailable', 'não encontrada': 'not found',
    'FC média: dados insuficientes': 'Average HR: insufficient data',
}

_REVERSE = {v: k for k, v in EN.items()}


def set_language(lang):
    global _CURRENT
    if lang not in LANGUAGES:
        raise ValueError('Invalid language: ' + str(lang))
    _CURRENT = lang


def get_language():
    return _CURRENT


def to_pt(value):
    return _REVERSE.get(value, value) if isinstance(value, str) else value


def t(value, lang=None):
    if not isinstance(value, str):
        return value
    source = to_pt(value)
    return EN.get(source, source) if (lang or _CURRENT) == 'en' else source


def translate_template(value, lang=None):
    """Translate known dynamic result strings without modifying user text."""
    language = lang or _CURRENT
    if language == 'pt_BR':
        return value
    exact = t(value, language)
    if exact != value:
        return exact
    replacements = (
        ('Excluir permanentemente ', 'Permanently delete '),
        ('Exclusão solicitada para ', 'Deletion requested for '),
        (' treinos.', ' workouts.'),
        ('Backup: ', 'Backup: '),
        ('Lotes com erro:', 'Failed batches:'),
        ('Exclusão solicitada', 'Deletion requested'),
        ('Consulte novamente para conferir.', 'Refresh the calendar to verify.'),
        (' eventos consultados; mostrando apenas WORKOUT.', ' events found; displaying only WORKOUT.'),
        (' treinos salvos em:', ' workouts saved to:'),
        (' treinos WORKOUT', ' WORKOUT events'),
        (' treinos planejados', ' planned workouts'),
        ('De ', 'From '), (' até ', ' to '),
        ('Um backup JSON será criado ANTES de excluir.', 'A JSON backup will be created BEFORE deletion.'),
        ('Atividades realizadas não serão excluídas.', 'Completed activities will not be deleted.'),
        ('Treinos existentes não serão substituídos.', 'Existing workouts will not be replaced.'),
        ('Antes de enviar, vamos conferir possíveis duplicatas no calendário.', 'We will check the calendar for duplicates before uploading.'),
        ('Criar ', 'Create '), (' treinos na SUA conta do Intervals.icu?', ' workouts in YOUR Intervals.icu account?'),
        (' treino(s) com a mesma data e nome já existem no Intervals.icu.', ' workouts with the same date and name already exist in Intervals.icu.'),
        ('O envio foi CANCELADO. Revise e remova as duplicatas antes de tentar.', 'Upload CANCELED. Resolve duplicates before trying again.'),
        (' treinos enviados sem erros HTTP.', ' workouts uploaded without HTTP errors.'),
        ('Confira o calendário remoto para confirmar a publicação.', 'Check your Intervals.icu calendar to confirm publication.'),
        (' eventos exportados para:', ' events exported to:'),
        ('Treinos CSV salvos em:', 'Workout CSV saved to:'),
        ('CSV exportado para:', 'CSV exported to:'),
        ('Confira o intervalo exportado no arquivo.', 'Check the dates inside the exported file.'),
        ('Plano salvo em:', 'Plan saved to:'),
        ('Plano salvo em ', 'Plan saved to '),
        (' treinos em ', ' workouts over '),
        (' semanas', ' weeks'), ('Dias: ', 'Days: '),
        ('Previsão: ', 'Projected end: '),
        ('PRAZO SOLICITADO CURTO', 'DEADLINE TOO SHORT'),
        ('Pasta criada:', 'Folder created:'),
        ('Arquivos: ', 'Files: '),
        ('RESUMO: ', 'SUMMARY: '),
        ('ORIENTAÇÕES GERAIS DO PLANO', 'GENERAL PLAN GUIDANCE'),
        ('Distância total aproximada: ', 'Approximate total distance: '),
        ('km. Em FC e zonas, o valor é uma projeção, não uma meta exata.', 'km. For HR/zones, this is a projection, not an exact target.'),
        (' corridas analisadas. Abra ‘Criar plano’ para aplicar o histórico.', ' runs analyzed. Open “Create plan” to use your history.'),
        ('Treino ', 'Workout '), (' tem data passada:', ' has a past date:'),
        ('Erro HTTP ', 'HTTP error '), ('Falha de rede: ', 'Network error: '),
    )
    out = value
    for src, dest in replacements:
        out = out.replace(src, dest)
    return out


class LocalizedMessages:
    """Drop-in tkinter.messagebox interface for commonly used dialog methods."""
    def __getattr__(self, method):
        from tkinter import messagebox
        original = getattr(messagebox, method)
        def wrapper(title, message, *args, **kwargs):
            return original(translate_template(title), translate_template(message), *args, **kwargs)
        return wrapper


messages = LocalizedMessages()


def localize_widget_tree(widget):
    """Live-update labels, tabs, headings and options without destroying user input."""
    from tkinter import ttk
    # Only translate UI widgets, never freeform Text or user-entered Entry values.
    try:
        if 'text' in widget.keys() and (
                'textvariable' not in widget.keys() or not widget.cget('textvariable')):
            widget.configure(text=t(widget.cget('text')))
    except Exception:
        pass
    if isinstance(widget, ttk.Notebook):
        for tab in widget.tabs():
            widget.tab(tab, text=t(widget.tab(tab, 'text')))
    if isinstance(widget, ttk.Treeview):
        for column in widget['columns']:
            label = widget.heading(column).get('text', '')
            widget.heading(column, text=t(label))
    if isinstance(widget, ttk.Combobox) and str(widget.cget('state')) == 'readonly':
        old_value = widget.get()
        vals = widget.cget('values')
        widget.configure(values=[t(v) for v in vals])
        new_value = t(old_value)
        if new_value != old_value:
            widget.set(new_value)
    for child in widget.winfo_children():
        localize_widget_tree(child)


def translate_guidance(text, lang='en'):
    """Translate static and parameterized guidance created by the rules engine."""
    if lang == 'pt_BR':
        return text
    exact = t(text, lang)
    if exact != text:
        return exact
    patterns = [
        (r'^FC: metas como percentuais de FCmax \(informada: (\d+) bpm\)\. %FCmax não é %FC de limiar; confirme as configurações do Intervals\.icu\.$',
         r'HR: goals are percentages of HRmax (entered: \1 bpm), not threshold HR. Confirm your Intervals.icu settings.'),
        (r'^Histórico API: (\d+) corridas em 8 semanas; ([\d.,]+) km/semana e ([\d.,]+) sessões/semana nas últimas 4 semanas\.$',
         r'API history: \1 runs in 8 weeks; \2 km/week and \3 sessions/week in the last 4 weeks.'),
        (r'^FC média mediana observada: (\d+) bpm\. Não usada como FCmax nem limiar\.$',
         r'Median average HR observed: \1 bpm. Not used as HRmax or threshold.'),
        (r'^PRAZO ALERTA: data-limite (\d\d/\d\d/\d{4}) é anterior à previsão (\d\d/\d\d/\d{4})\. O sistema NÃO acelera a carga para encaixar no prazo\.$',
         r'DEADLINE WARNING: requested deadline \1 precedes projected completion \2. Training load will NOT be rushed.'),
        (r'^Data-limite (\d\d/\d\d/\d{4}): a projeção encerra antes desse prazo\. A evolução individual pode exigir mais tempo\.$',
         r'Deadline \1: the plan ends sooner, though individual progress may take longer.'),
    ]
    for pattern, replacement in patterns:
        if re.fullmatch(pattern, text):
            return re.sub(pattern, replacement, text)
    return text


def localize_plan(plan, lang=None):
    """Return a translated copy of a generated plan. Never touch API field identifiers.

    The source plan MUST be the canonical Portuguese output from generate_plan.
    A plan already edited by the user should not be passed here.
    """
    from copy import deepcopy
    language = lang or _CURRENT
    result = deepcopy(plan)
    result['language'] = language
    if language == 'pt_BR':
        return result
    result['chosen_days'] = [t(d, language) for d in result['chosen_days']]
    result['warnings'] = [translate_guidance(w, language) for w in result['warnings']]
    for event in result['events']:
        kind = t(event['_kind'], language)
        event['_kind'] = kind
        event['_phase'] = t(event['_phase'], language)
        title_start = event['name'].rsplit(' - ', 1)[0]
        title_start = re.sub(r'(?<=\d),(?=\d+km/)', '.', title_start)
        event['name'] = title_start + ' - ' + kind
        event['_note'] = t(event['_note'], language)
        lines = event['description'].split('\n')
        translated = []
        for i, line in enumerate(lines):
            if i == 0 and line.startswith('Dica: '):
                translated.append('Tip: ' + t(line[6:], language))
            elif line and not line.startswith('- ') and not re.fullmatch(r'\d+x', line):
                translated.append(t(line, language))
            else:
                translated.append(line)
        event['description'] = '\n'.join(translated)
    return result
