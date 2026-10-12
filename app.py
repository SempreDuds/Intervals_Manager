"""Intervals Manager: gerenciador local de treinos Intervals.icu."""
import csv
import json
import os
import threading
from datetime import date, timedelta, datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
from i18n import t, to_pt, set_language, get_language, LANGUAGES, localize_widget_tree, translate_template, messages as messagebox
from gerador_ui import GeneratorTab
from visual import activate, BG, PANEL, TEXT, MUTED, ACCENT, text_box

try:
    import requests
except ImportError:
    raise SystemExit('Instale requests: py -m pip install requests')

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / 'config.json'
BACKUPS = ROOT / 'backups'
EXPORTS = ROOT / 'exportacoes'
PLANS = ROOT / 'planos'
for p in (BACKUPS, EXPORTS, PLANS):
    p.mkdir(parents=True, exist_ok=True)
BASE = 'https://intervals.icu/api/v1/athlete/0'

def day(s):
    return date.fromisoformat(str(s)[:10])

class API:
    def __init__(self, key):
        if not key.strip():
            raise ValueError('Informe sua API Key em Configuração.')
        self.key = key.strip()
        self.session = requests.Session()
        self.session.auth = ('API_KEY', self.key)
        self.session.headers['User-Agent'] = 'IntervalsManager/4.0'

    def call(self, method, path, **kwargs):
        try:
            r = self.session.request(method, BASE + path, timeout=45, **kwargs)
            r.raise_for_status()
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else '?' 
            body = (e.response.text if e.response is not None else '')[:400]
            raise RuntimeError(f'Erro HTTP {status}: {body}') from e
        except requests.RequestException as e:
            raise RuntimeError(f'Falha de rede: {e}') from e
        if r.status_code == 204 or not r.content:
            return None
        if 'json' in r.headers.get('Content-Type', ''):
            return r.json()
        return r.content

    def events(self, start, end):
        return self.call('GET', '/events', params={'oldest': start, 'newest': end})

    def activities(self, start, end):
        result = self.call('GET', '/activities', params={'oldest':start, 'newest':end})
        if not isinstance(result, list):
            raise ValueError('O Intervals.icu não retornou uma lista de atividades válida.')
        return result

    def activities_csv(self, start, end):
        # CSV endpoint is documented; date-filtering is handled locally if necessary.
        return self.call('GET', '/activities.csv', params={'oldest': start, 'newest': end})

    def bulk_create(self, events):
        return self.call('POST', '/events/bulk', json=events, params={'upsert': 'false'})

    def bulk_delete(self, ids):
        return self.call('PUT', '/events/bulk-delete', json=[{'id': x} for x in ids])

    def delete_one(self, eid):
        return self.call('DELETE', f'/events/{eid}')

class App:
    def __init__(self, root):
        self.root = root
        root.title(t('Intervals Manager 4.0 | Seu estúdio de corrida'))
        root.geometry('1230x790')
        root.minsize(1010, 650)
        self.config = self.read_config()
        set_language(self.config.get('language', 'pt_BR') if self.config.get('language') in LANGUAGES else 'pt_BR')
        self.language_choice = tk.StringVar(value=LANGUAGES[get_language()])
        self.api_key = tk.StringVar(value=self.config.get('api_key', ''))
        self.start = tk.StringVar(value=date.today().isoformat())
        self.end = tk.StringVar(value=(date.today() + timedelta(days=365)).isoformat())
        self.future_only = tk.BooleanVar(value=True)
        self.events_cache = []
        self.plan_path = None
        self.plan_events = []
        self.plan_metadata = {}
        self.editor_selected = None
        self.status = tk.StringVar(value=t('Pronto. Configure a API Key na primeira aba.'))
        self.build()

    def read_config(self):
        if CONFIG.exists():
            try: return json.loads(CONFIG.read_text(encoding='utf-8'))
            except (ValueError, OSError): pass
        return {}

    def api(self):
        return API(self.api_key.get())

    def work(self, label, task, success=None, on_error=None):
        self.status.set(translate_template(label))
        def background():
            try:
                result = task()
                self.root.after(0, lambda: (self.status.set(t('Concluído.')), success(result) if success else None))
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda: (on_error() if on_error else None, self.status.set(t('Erro') + ': ' + translate_template(msg)), messagebox.showerror('Erro', msg)))
        threading.Thread(target=background, daemon=True).start()

    def build(self):
        activate(self.root)
        head = ttk.Frame(self.root, style='Header.TFrame', padding=(27, 20))
        head.pack(fill='x')
        mark = tk.Canvas(head, width=43, height=43, highlightthickness=0, background=PANEL)
        mark.create_oval(2, 2, 41, 41, fill=ACCENT, outline='')
        mark.create_text(21, 22, text=t('↗'), fill='#062623', font=('Segoe UI', 21, 'bold'))
        mark.pack(side='left', padx=(0, 12))
        titlebox = ttk.Frame(head, style='Header.TFrame')
        titlebox.pack(side='left')
        ttk.Label(titlebox, text=t('INTERVALS  /  MANAGER'), style='Header.TLabel',
                  font=('Segoe UI Semibold', 18)).pack(anchor='w')
        ttk.Label(titlebox, text=t('Treino inteligente, no seu ritmo'), style='Header.TLabel',
                  foreground='#A6BACF').pack(anchor='w')
        ttk.Label(head, text=t('v4.0  •  WINDOWS + PYTHON'), style='Header.TLabel',
                  foreground=ACCENT, font=('Segoe UI Semibold', 10)).pack(side='right')
        langbar = ttk.Frame(head, style='Header.TFrame')
        langbar.pack(side='right', padx=(0, 22))
        ttk.Label(langbar, text=t('Idioma'), style='Header.TLabel').pack(side='left', padx=(0, 9))
        self.language_selector = ttk.Combobox(langbar, textvariable=self.language_choice,
             values=list(LANGUAGES.values()), state='readonly', width=21)
        self.language_selector.pack(side='left')
        self.language_selector.bind('<<ComboboxSelected>>', self.change_language)
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill='both', expand=True, padx=24, pady=(18, 12))
        self.tab_config = ttk.Frame(self.nb, padding=22)
        self.tab_calendar = ttk.Frame(self.nb, padding=22)
        self.tab_plan = ttk.Frame(self.nb, padding=22)
        self.tab_tools = ttk.Frame(self.nb, padding=22)
        self.tab_generator = ttk.Frame(self.nb, padding=22)
        for widget, name in [(self.tab_generator, '  Gerador  '),
                              (self.tab_calendar, '  Calendário  '),
                              (self.tab_plan, '  Meus planos  '),
                              (self.tab_tools, '  Exportações  '),
                              (self.tab_config, '  Conexão  ')]:
            self.nb.add(widget, text=t(name))
        ttk.Label(self.root, textvariable=self.status, anchor='w',
                  style='Subtitle.TLabel', padding=(25, 11)).pack(fill='x', side='bottom')
        self.build_config()
        self.build_calendar()
        self.generator = GeneratorTab(self, self.tab_generator, PLANS)
        self.build_plan()
        self.build_tools()
        self.nb.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        if not self.api_key.get():
            self.nb.select(self.tab_config)
        else:
            self.root.after(450, self._on_tab_changed)

    def change_language(self, _event=None):
        selected = next((code for code, label in LANGUAGES.items()
                         if label == self.language_choice.get()), 'pt_BR')
        if selected == get_language():
            return
        set_language(selected)
        self.config['language'] = selected
        # No external API request and no changes to unsaved editor contents.
        CONFIG.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding='utf-8')
        if os.name != 'nt':
            os.chmod(CONFIG, 0o600)
        self.root.title(t('Intervals Manager 4.0 | Seu estúdio de corrida'))
        localize_widget_tree(self.root)
        self.status.set(t('Pronto. Configure a API Key na primeira aba.'))
        if hasattr(self, 'generator'):
            self.generator.relocalize()
        if self.plan_path is None:
            self.refresh_plan()

    def _on_tab_changed(self, _event=None):
        # Leitura automática apenas no Gerador e só depois da configuração local.
        if (self.nb.select() == str(self.tab_generator)
                and self.api_key.get().strip()
                and not self.generator.auto_attempted):
            self.generator.fetch_activities()

    def build_config(self):
        f = self.tab_config
        ttk.Label(f, text=t('Conectar ao Intervals.icu'), font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(f, text=t('Sua API Key fica armazenada apenas neste computador, no arquivo config.json. Não compartilhe este arquivo.')).pack(anchor='w', pady=7)
        ttk.Label(f, text=t('API Key (Intervals.icu → Settings → API key)')).pack(anchor='w')
        ttk.Entry(f, textvariable=self.api_key, show='•', width=65).pack(anchor='w', fill='x', pady=6)
        buttons = ttk.Frame(f)
        buttons.pack(anchor='w', pady=9)
        ttk.Button(buttons, text=t('Salvar chave'), command=self.save_key).pack(side='left', padx=(0, 8))
        ttk.Button(buttons, text=t('Testar conexão'), style='Accent.TButton', command=self.test_connection).pack(side='left')
        ttk.Label(f, text=t('Importante: para excluir eventos, a sua chave precisa ter permissão de acesso ao calendário.'), wraplength=720).pack(anchor='w', pady=14)
        ttk.Button(f, text=t('Abrir site do Intervals.icu'), command=lambda: __import__('webbrowser').open('https://intervals.icu/settings')).pack(anchor='w')

    def save_key(self):
        self.config['api_key'] = self.api_key.get().strip()
        CONFIG.write_text(json.dumps(self.config, indent=2), encoding='utf-8')
        # Reduce accidental key exposure on Unix; Windows file ACL follows user profile permissions.
        if os.name != 'nt': os.chmod(CONFIG, 0o600)
        messagebox.showinfo('Configuração', 'Chave salva localmente. Guarde o arquivo config.json em segurança.')

    def test_connection(self):
        self.work('Testando conexão...', lambda: self.api().events(date.today().isoformat(), (date.today()+timedelta(days=7)).isoformat()), lambda _ : messagebox.showinfo('Conexão', 'Conexão funcionando!'))

    def build_calendar(self):
        f = self.tab_calendar
        ttk.Label(f, text=t('Calendário e exclusão em massa'), font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 8))
        controls = ttk.Frame(f)
        controls.pack(fill='x', pady=(0, 8))
        ttk.Label(controls, text=t('De:')).pack(side='left')
        ttk.Entry(controls, textvariable=self.start, width=13).pack(side='left', padx=5)
        ttk.Label(controls, text=t('Até:')).pack(side='left', padx=(15, 0))
        ttk.Entry(controls, textvariable=self.end, width=13).pack(side='left', padx=5)
        ttk.Button(controls, text=t('Consultar'), style='Accent.TButton', command=self.load_calendar).pack(side='left', padx=12)
        ttk.Checkbutton(controls, text=t('Apenas treinos de hoje em diante'), variable=self.future_only, command=self.render_calendar).pack(side='left')
        self.tree = ttk.Treeview(f, columns=('date', 'type', 'name', 'id'), show='headings', selectmode='extended')
        for key, title, width in [('date', 'Data', 135), ('type', 'Modalidade', 125), ('name', 'Treino', 510), ('id', 'ID', 95)]:
            self.tree.heading(key, text=t(title))
            self.tree.column(key, width=width, stretch=(key == 'name'))
        self.tree.pack(fill='both', expand=True)
        bar = ttk.Frame(f)
        bar.pack(fill='x', pady=(12, 0))
        ttk.Button(bar, text=t('Backup dos treinos exibidos'), command=self.backup_visible).pack(side='left', padx=(0, 8))
        ttk.Button(bar, text=t('Excluir selecionados'), command=self.delete_selected).pack(side='left', padx=8)
        ttk.Button(bar, text=t('EXCLUIR TODOS OS FUTUROS'), style='Danger.TButton', command=self.delete_future).pack(side='right')
        ttk.Label(f, text=t('A exclusão só atinge eventos WORKOUT do calendário; atividades realizadas não são apagadas. Backup é obrigatório antes da exclusão.'), wraplength=930).pack(anchor='w', pady=8)

    def range_dates(self):
        start, end = day(self.start.get()), day(self.end.get())
        if start > end: raise ValueError('Data inicial posterior à final.')
        if (end - start).days > 3650: raise ValueError('Limite de consulta: 10 anos.')
        return start.isoformat(), end.isoformat()

    def load_calendar(self):
        try: start, end = self.range_dates()
        except Exception as e:
            messagebox.showerror('Datas', str(e)); return
        self.work('Consultando calendário...', lambda: self.api().events(start, end), self.loaded)

    def loaded(self, events):
        self.events_cache = events if isinstance(events, list) else []
        self.render_calendar()
        messagebox.showinfo('Calendário', f'{len(self.events_cache)} eventos consultados; mostrando apenas WORKOUT.')

    def visible_events(self):
        today = date.today()
        return [e for e in self.events_cache if e.get('category') == 'WORKOUT' and (not self.future_only.get() or (e.get('start_date_local') and day(e['start_date_local']) >= today))]

    def render_calendar(self):
        for row in self.tree.get_children(): self.tree.delete(row)
        for e in sorted(self.visible_events(), key=lambda e: e.get('start_date_local', '')):
            self.tree.insert('', 'end', iid=str(e['id']), values=(e.get('start_date_local', '')[:10], e.get('type', ''), e.get('name', ''), e['id']))

    def backup_events(self, events, tag='treinos'):
        filename = f'{tag}_{datetime.now():%Y%m%d_%H%M%S_%f}.json'
        path = BACKUPS / filename
        payload = {'app': 'Intervals Manager', 'created_at': datetime.now().isoformat(), 'events': events}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        return path

    def backup_visible(self):
        ev = self.visible_events()
        if not ev: messagebox.showinfo('Backup', 'Não há treinos exibidos. Consulte o calendário.'); return
        path = self.backup_events(ev)
        messagebox.showinfo('Backup', f'{len(ev)} treinos salvos em:\n{path}')

    def delete_selected(self):
        ids = {int(i) for i in self.tree.selection()}
        self.perform_delete([e for e in self.visible_events() if e.get('id') in ids])

    def delete_future(self):
        # Always requery all future workouts, not just the UI's cached subset.
        start = date.today().isoformat()
        # Broad horizon explicitly displayed for confirmation; calendar may contain workouts after it.
        end = '2100-12-31'
        def ready(evs):
            target = [e for e in evs if e.get('category') == 'WORKOUT' and e.get('id') is not None and e.get('start_date_local', '')[:10] >= start]
            self.perform_delete(target)
        self.work('Buscando treinos futuros até 2100...', lambda: self.api().events(start, end), ready)

    def perform_delete(self, events):
        events = [e for e in events if e.get('id') is not None]
        if not events:
            messagebox.showinfo('Sem treinos', 'Nenhum treino planejado elegível para exclusão.'); return
        earliest = min(e.get('start_date_local', '')[:10] for e in events)
        latest = max(e.get('start_date_local', '')[:10] for e in events)
        if not messagebox.askyesno('Confirmar EXCLUSÃO', f'Excluir permanentemente {len(events)} treinos WORKOUT\nDe {earliest} até {latest}?\n\nUm backup JSON será criado ANTES de excluir.\nAtividades realizadas não serão excluídas.', icon='warning'):
            return
        backup = self.backup_events(events, 'ANTES_DA_EXCLUSAO')
        ids = [e['id'] for e in events]
        def run():
            # Deletion by exact ID is safer than date-range category deletion.
            # Batch to avoid large request bodies; report progress/failures accurately.
            succeeded = []
            errors = []
            for i in range(0, len(ids), 100):
                batch = ids[i:i+100]
                try:
                    self.api().bulk_delete(batch)
                    succeeded.extend(batch)
                except Exception as exc:
                    errors.append(f'Lote {i//100+1}: {exc}')
            return succeeded, errors, backup
        def finish(result):
            succeeded, errors, path = result
            self.events_cache = [e for e in self.events_cache if e.get('id') not in set(succeeded)]
            self.render_calendar()
            note = f'Exclusão solicitada para {len(succeeded)} treinos.\nBackup: {path}'
            if errors: note += '\n\nLotes com erro:\n' + '\n'.join(errors)
            messagebox.showwarning('Resultado parcial', note) if errors else messagebox.showinfo('Resultado', note + '\n\nConsulte novamente para conferir.')
        self.work('Excluindo treinos com backup...', run, finish)

    def build_plan(self):
        f = self.tab_plan
        ttk.Label(f, text=t('Planos locais: editar, salvar e importar'), font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 8))
        top = ttk.Frame(f)
        top.pack(fill='x', pady=5)
        for name, cmd in [('Novo plano', self.new_plan), ('Abrir JSON/CSV', self.open_plan), ('Salvar JSON', self.save_plan), ('Enviar à API', self.upload_plan)]:
            ttk.Button(top, text=t(name), command=cmd).pack(side='left', padx=(0, 7))
        self.plan_label = ttk.Label(f, text=t('Plano não aberto'))
        self.plan_label.pack(anchor='w', pady=5)
        work = ttk.Panedwindow(f, orient='horizontal')
        work.pack(fill='both', expand=True)
        left = ttk.Frame(work)
        right = ttk.Frame(work)
        work.add(left, weight=1)
        work.add(right, weight=2)
        self.plan_list = tk.Listbox(left, exportselection=False, width=34)
        self.plan_list.pack(fill='both', expand=True)
        self.plan_list.bind('<<ListboxSelect>>', self.pick_plan)
        b = ttk.Frame(left)
        b.pack(fill='x', pady=6)
        ttk.Button(b, text=t('Adicionar treino'), command=self.add_workout).pack(side='left', padx=(0, 5))
        ttk.Button(b, text=t('Remover'), command=self.remove_workout).pack(side='left')
        fields = ttk.Frame(right)
        fields.pack(fill='x')
        ttk.Label(fields, text=t('Data (AAAA-MM-DD)')).grid(row=0, column=0, sticky='w')
        ttk.Label(fields, text=t('Modalidade')).grid(row=0, column=1, sticky='w', padx=8)
        self.plan_date = tk.StringVar()
        self.plan_type = tk.StringVar(value='Run')
        ttk.Entry(fields, textvariable=self.plan_date, width=18).grid(row=1, column=0, sticky='ew')
        ttk.Combobox(fields, textvariable=self.plan_type, state='readonly', values=['Run', 'Ride', 'Swim', 'Walk', 'WeightTraining', 'Other'], width=20).grid(row=1, column=1, padx=8, sticky='ew')
        ttk.Label(right, text=t('Título')).pack(anchor='w', pady=(6, 0))
        self.plan_name = tk.StringVar()
        ttk.Entry(right, textvariable=self.plan_name).pack(fill='x')
        ttk.Label(right, text=t('Descrição do treino (linguagem nativa do Intervals.icu)')).pack(anchor='w', pady=(8, 0))
        self.plan_description = tk.Text(right, height=13, font=('Consolas', 10), wrap='word')
        text_box(self.plan_description)
        self.plan_description.pack(fill='both', expand=True)
        ttk.Button(right, text=t('Aplicar alterações neste treino'), command=self.apply_workout).pack(fill='x', pady=7)
        ttk.Label(f, text=t('Dica: inclua uma data diferente em cada treino. Ao enviar, o aplicativo cria eventos novos; não substitui treinos existentes.')).pack(anchor='w')

    def new_plan(self):
        if self.plan_events and not messagebox.askyesno('Novo plano', 'Descartar plano ainda aberto? Salve primeiro se necessário.'):
            return
        self.plan_events = []
        self.plan_metadata = {}
        self.plan_path = None
        self.editor_selected = None
        self.refresh_plan()

    def open_plan(self):
        p = filedialog.askopenfilename(initialdir=PLANS, filetypes=[('Planos JSON/CSV', '*.json *.csv')])
        if not p: return
        try:
            path = Path(p)
            if path.suffix.lower() == '.json':
                data = json.loads(path.read_text(encoding='utf-8-sig'))
                items = data if isinstance(data, list) else data.get('events', data.get('treinos', []))
                meta = {k:v for k,v in data.items() if k != 'events'} if isinstance(data, dict) else {}
            else:
                with path.open('r', encoding='utf-8-sig', newline='') as file:
                    items = list(csv.DictReader(file))
                meta = {}
            converted = []
            for e in items:
                raw_date = e.get('start_date_local') or e.get('date') or e.get('data')
                if not raw_date: raise ValueError('Treino sem data: use start_date_local, date ou data.')
                converted.append({'category': 'WORKOUT', 'start_date_local': day(raw_date).isoformat()+'T00:00:00', 'type': e.get('type') or 'Run', 'name': e.get('name') or t('Treino'), 'description': e.get('description') or ''})
            self.plan_events = converted
            self.plan_metadata = meta
            self.plan_path = path if path.suffix.lower() == '.json' else None
            self.editor_selected = None
            self.refresh_plan()
        except Exception as e: messagebox.showerror('Abrir plano', str(e))

    def save_plan(self):
        if not self.plan_events:
            messagebox.showinfo('Salvar', 'Adicione pelo menos um treino.'); return
        default = self.plan_path.name if self.plan_path else 'meu_plano.json'
        path = filedialog.asksaveasfilename(initialdir=PLANS, initialfile=default, defaultextension='.json', filetypes=[('Plano JSON', '*.json')])
        if not path: return
        data = {'format': 'intervals-manager-plan-v2', **self.plan_metadata, 'events': self.plan_events}
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        self.plan_path = Path(path)
        self.refresh_plan()
        messagebox.showinfo('Salvo', f'Plano salvo em:\n{path}')

    def refresh_plan(self):
        self.plan_list.delete(0, 'end')
        for e in self.plan_events:
            self.plan_list.insert('end', f"{e['start_date_local'][:10]} | {e['name']}")
        self.plan_label.configure(text=str(self.plan_path) if self.plan_path else t('Plano novo (ainda não salvo)'))

    def add_workout(self):
        e = {'category': 'WORKOUT', 'start_date_local': (date.today()+timedelta(days=1)).isoformat()+'T00:00:00', 'type': 'Run', 'name': t('Novo treino'), 'description': 'Warmup\n- 10m Z1\n\nMain set\n- 20m Z2\n\nCooldown\n- 5m Z1'}
        self.plan_events.append(e)
        self.refresh_plan()
        ix = len(self.plan_events) - 1
        self.plan_list.selection_set(ix)
        self.pick_plan()

    def pick_plan(self, event=None):
        selection = self.plan_list.curselection()
        if not selection: return
        self.editor_selected = selection[0]
        e = self.plan_events[self.editor_selected]
        self.plan_date.set(e['start_date_local'][:10])
        self.plan_name.set(e['name'])
        self.plan_type.set(e['type'])
        self.plan_description.delete('1.0', 'end')
        self.plan_description.insert('1.0', e.get('description', ''))

    def apply_workout(self):
        if self.editor_selected is None: messagebox.showwarning('Editar', 'Selecione um treino.'); return
        try: start = day(self.plan_date.get()).isoformat()
        except ValueError: messagebox.showerror('Data', 'Use uma data válida: AAAA-MM-DD'); return
        self.plan_events[self.editor_selected] = {'category':'WORKOUT','start_date_local':start+'T00:00:00', 'type':self.plan_type.get(), 'name':self.plan_name.get().strip() or t('Treino'), 'description':self.plan_description.get('1.0','end-1c')}
        index = self.editor_selected
        self.refresh_plan()
        self.plan_list.selection_set(index)
        self.status.set(t('Treino atualizado na memória. Clique em Salvar JSON para gravar no disco.'))

    def remove_workout(self):
        selection = self.plan_list.curselection()
        if not selection: return
        self.plan_events.pop(selection[0])
        self.editor_selected = None
        self.refresh_plan()

    def load_generated_plan(self, generated, json_path=None):
        """Importar do gerador para o editor local (sem enviar pela rede)."""
        if self.plan_events and not messagebox.askyesno(
                'Abrir no editor',
                'O editor contém outro plano. Salve-o antes de substituir. Continuar?'):
            return
        self.plan_events = [dict(e) for e in generated['events']]
        self.plan_metadata = {k:v for k,v in generated.items() if k not in ('events', '_last_saved_path')}
        self.plan_path = json_path
        self.editor_selected = None
        self.refresh_plan()
        self.nb.select(self.tab_plan)
        self.status.set(t('Plano do gerador carregado no editor. Revise, salve e só então envie à API.'))

    def upload_plan(self):
        if not self.plan_events:
            messagebox.showwarning('Importação', 'Abra ou crie um plano primeiro.'); return
        try:
            events = []
            for e in self.plan_events:
                on = day(e['start_date_local'])
                if on < date.today():
                    raise ValueError(f"O treino {e.get('name', '')} tem data passada: {on}")
                events.append({k:e.get(k) for k in ('category','start_date_local','type','name','description')})
            if len(events) != len({(e['start_date_local'][:10], e['name']) for e in events}):
                raise ValueError('O plano contém datas e títulos duplicados. Revise primeiro.')
        except Exception as ex:
            messagebox.showerror('Plano inválido', str(ex)); return
        if not messagebox.askyesno('Enviar plano',
                f'Criar {len(events)} treinos na SUA conta do Intervals.icu?\n\n'
                'Treinos existentes não serão substituídos.\n'
                'Antes de enviar, vamos conferir possíveis duplicatas no calendário.'):
            return
        start = min(e['start_date_local'][:10] for e in events)
        end = max(e['start_date_local'][:10] for e in events)
        def checked(existing):
            existing_keys = {(x.get('start_date_local','')[:10],x.get('name','')) for x in existing if x.get('category') == 'WORKOUT'}
            duplicates = [e for e in events if (e['start_date_local'][:10], e['name']) in existing_keys]
            if duplicates:
                messagebox.showwarning('Duplicatas detectadas',
                    f'{len(duplicates)} treino(s) com a mesma data e nome já existem no Intervals.icu.\n'
                    'O envio foi CANCELADO. Revise e remova as duplicatas antes de tentar.')
                return
            def upload():
                count=0
                for i in range(0,len(events),50):
                    # O retorno pode ser lista, objeto ou vazio; contamos eventos enviados
                    # e informamos que o usuario deve conferir o calendario depois.
                    self.api().bulk_create(events[i:i+50])
                    count+=len(events[i:i+50])
                return count
            self.work('Enviando treinos para o Intervals.icu...', upload,
                lambda n: messagebox.showinfo('Envio solicitado',
                    f'{n} treinos enviados sem erros HTTP.\nConfira o calendário remoto para confirmar a publicação.'))
        self.work('Conferindo possíveis duplicatas...', lambda: self.api().events(start,end), checked)

    def build_tools(self):
        f = self.tab_tools
        ttk.Label(f, text=t('Ferramentas de exportação'), font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(f, text=t('As datas da consulta são as mesmas definidas na aba Calendário.')).pack(anchor='w', pady=4)
        ttk.Button(f, text=t('Exportar calendário completo (JSON)'), command=self.export_calendar).pack(anchor='w', pady=9)
        ttk.Button(f, text=t('Exportar treinos planejados (CSV)'), command=self.export_workouts_csv).pack(anchor='w', pady=9)
        ttk.Button(f, text=t('Exportar atividades realizadas (CSV)'), command=self.export_activities).pack(anchor='w', pady=9)
        ttk.Button(f, text=t('Abrir pasta de planos'), command=lambda: self.open_folder(PLANS)).pack(anchor='w', pady=9)
        ttk.Button(f, text=t('Abrir pasta de backups'), command=lambda: self.open_folder(BACKUPS)).pack(anchor='w', pady=9)
        ttk.Label(f, text=t('Os backups JSON preservam dados do calendário, inclusive campos extras, para consulta. Ao abrir um backup como plano, apenas os campos essenciais são importados.')).pack(anchor='w', pady=10)

    def open_folder(self, folder):
        if os.name == 'nt': os.startfile(folder)
        else: __import__('subprocess').Popen(['xdg-open', str(folder)])

    def export_calendar(self):
        try: start, end = self.range_dates()
        except Exception as e: messagebox.showerror('Data', str(e)); return
        def finished(events):
            path = EXPORTS / f'calendario_{start}_{end}.json'
            path.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding='utf-8')
            messagebox.showinfo('Exportação', f'{len(events)} eventos exportados para:\n{path}')
        self.work('Exportando calendário...', lambda: self.api().events(start, end), finished)

    def export_workouts_csv(self):
        try: start, end = self.range_dates()
        except Exception as e: messagebox.showerror('Data', str(e)); return
        def finished(events):
            path = EXPORTS / f'treinos_{start}_{end}.csv'
            with path.open('w', encoding='utf-8-sig', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=['date','type','name','description'])
                writer.writeheader()
                for e in events:
                    if e.get('category') == 'WORKOUT':
                        writer.writerow({'date': e.get('start_date_local','')[:10], 'type':e.get('type',''), 'name':e.get('name',''), 'description':e.get('description','')})
            messagebox.showinfo('Exportação', f'Treinos CSV salvos em:\n{path}')
        self.work('Exportando treinos...', lambda: self.api().events(start, end), finished)

    def export_activities(self):
        try: start, end = self.range_dates()
        except Exception as e: messagebox.showerror('Data', str(e)); return
        def finished(result):
            path = EXPORTS / f'atividades_{start}_{end}.csv'
            path.write_bytes(result if isinstance(result, bytes) else str(result).encode('utf-8'))
            messagebox.showinfo('Atividades', f'CSV exportado para:\n{path}\n\nConfira o intervalo exportado no arquivo.')
        self.work('Exportando atividades...', lambda: self.api().activities_csv(start, end), finished)

if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
