"""Interface Tkinter do assistente para gerar planos de corrida."""
from __future__ import annotations

import csv
import json
import re
from datetime import date, timedelta
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog
from i18n import t, to_pt, get_language, translate_template, localize_widget_tree, localize_plan, messages as messagebox

from gerador_plano import PlanRequest, GOALS, METHODS, WEEKDAY_LABELS, generate_plan, fmt_pace
from analise_atividades import analyze_activities, summary_lines
from visual import MUTED, PANEL, ACCENT, text_box


def _field(frame, row, label, variable, width=32, help_text=None):
    ttk.Label(frame, text=t(label)).grid(row=row, column=0, sticky='w', padx=(4, 16), pady=6)
    ent = ttk.Entry(frame, textvariable=variable, width=width)
    ent.grid(row=row, column=1, sticky='ew', pady=6)
    if help_text:
        ttk.Label(frame, text=t(help_text), style="Muted.TLabel", wraplength=250).grid(row=row, column=2, sticky='w', padx=10)
    return ent


class PlanWizard(tk.Toplevel):
    def __init__(self, parent, on_generate, activity_stats=None):
        super().__init__(parent)
        self.title(t('Entrevista — Gerador de plano de corrida'))
        self.geometry('940x665')
        self.minsize(830, 600)
        self.transient(parent)
        self.on_generate = on_generate
        self.activity_stats = activity_stats
        self.name = tk.StringVar(value=t('Meu plano 5 km'))
        self.goal = tk.StringVar(value=t(GOALS[0]))
        self.distance = tk.StringVar(value='5')
        self.longest = tk.StringVar(value='2')
        self.speed_units = tk.StringVar(value=t('Pace (min/km)'))
        self.current_pace = tk.StringVar(value='08:00')
        self.target_pace = tk.StringVar(value='07:30')
        self.days = tk.StringVar(value='3')
        self.available = [tk.BooleanVar(value=i in (1, 3, 5)) for i in range(7)]
        self.start = tk.StringVar(value=(date.today() + timedelta(days=1)).isoformat())
        self.deadline = tk.StringVar(value=(date.today() + timedelta(weeks=16)).isoformat())
        self.method = tk.StringVar(value=t(METHODS[2]))
        self.max_hr = tk.StringVar(value='')
        self.training = tk.StringVar(value=t('Regular (1-3 meses)'))
        self.discomfort = tk.BooleanVar(value=False)
        if activity_stats:
            if activity_stats.get('valid_runs_8w', 0) >= 4 and activity_stats.get('estimated_recent_pace_seconds'):
                self.current_pace.set(fmt_pace(activity_stats['estimated_recent_pace_seconds']))
                if activity_stats.get('weekly_runs_4w', 0) >= 2:
                    self.training.set(t('Regular (1-3 meses)'))
                else:
                    self.training.set(t('Iniciante / parado'))
            # Nao use a maior atividade como a maior distancia SEM caminhar.
            self.longest.set('')
        self.configure(bg='#0B1220')
        self._build()
        self.grab_set()

    def _build(self):
        outer = ttk.Frame(self, padding=14)
        outer.pack(fill='both', expand=True)
        ttk.Label(outer, text=t('Responda às perguntas para personalizar sua programação'), font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        ttk.Label(outer, text=t('Os valores abaixo são só exemplos. Altere conforme seu nível real; o gerador funciona offline.'), wraplength=800).pack(anchor='w', pady=(4, 12))
        if self.activity_stats:
            ttk.Label(outer, text=t('Dados reais carregados • confira a maior distância SEM caminhar'),
                      style='Subtitle.TLabel', wraplength=840).pack(anchor='w', pady=(0, 10))
        self.tabs = ttk.Notebook(outer)
        self.tabs.pack(fill='both', expand=True)
        first, second, third = (ttk.Frame(self.tabs, padding=16) for _ in range(3))
        for f, title in ((first, '1. Objetivo e nível'), (second, '2. Dias e prazo'), (third, '3. Intensidade e cuidados')):
            self.tabs.add(f, text=t(title))
            f.columnconfigure(1, weight=1)
        _field(first, 0, 'Nome do plano', self.name, help_text='Ex.: 5 km sem parar — Primavera')
        ttk.Label(first, text=t('Principal objetivo')).grid(row=1, column=0, sticky='w', pady=6)
        ttk.Combobox(first, textvariable=self.goal, values=[t(x) for x in GOALS], state='readonly', width=30).grid(row=1, column=1, sticky='ew', pady=6)
        _field(first, 2, 'Distância alvo (km)', self.distance, help_text='Ex.: 3, 4, 5, 10. Aceita vírgula.')
        _field(first, 3, 'Maior distância sem caminhar (km)', self.longest, help_text='Use 0 se ainda não corre continuamente.')
        ttk.Label(first, text=t('Informar ritmos como')).grid(row=4, column=0, sticky='w', pady=6)
        unitbox = ttk.Combobox(first, textvariable=self.speed_units, values=[t('Pace (min/km)'), t('Velocidade (km/h)')], state='readonly', width=30)
        unitbox.grid(row=4, column=1, sticky='ew', pady=6)
        unitbox.bind('<<ComboboxSelected>>', self.switch_speed_units)
        self.current_label = ttk.Label(first, text=t('Pace atual (min/km)'))
        self.current_label.grid(row=5, column=0, sticky='w', padx=(4, 16), pady=6)
        ttk.Entry(first, textvariable=self.current_pace, width=32).grid(row=5, column=1, sticky='ew', pady=6)
        self.target_label = ttk.Label(first, text=t('Pace objetivo (min/km)'))
        self.target_label.grid(row=6, column=0, sticky='w', padx=(4, 16), pady=6)
        ttk.Entry(first, textvariable=self.target_pace, width=32).grid(row=6, column=1, sticky='ew', pady=6)
        ttk.Label(first, text=t('Ex.: 08:00 min/km ou 7,5 km/h'), style="Muted.TLabel").grid(row=6, column=2, sticky='w', padx=10)
        ttk.Label(first, text=t('Histórico recente de corrida')).grid(row=7, column=0, sticky='w', pady=6)
        ttk.Combobox(first, textvariable=self.training, values=[t(x) for x in ['Iniciante / parado', 'Regular (1-3 meses)', 'Regular (>3 meses)']], state='readonly', width=30).grid(row=7, column=1, sticky='ew', pady=6)
        ttk.Label(first, text=t('Exemplo: ritmo atual de 08:00 min/km significa 7,5 km/h. Para ficar mais rápido, o pace alvo deve ser MENOR.'), wraplength=670, style="Muted.TLabel").grid(row=8, column=0, columnspan=3, sticky='w', pady=16)

        ttk.Label(second, text=t('Quantos treinos por semana?')).grid(row=0, column=0, sticky='w', pady=7)
        ttk.Combobox(second, textvariable=self.days, values=['2','3','4','5'], state='readonly', width=13).grid(row=0, column=1, sticky='w', pady=7)
        ttk.Label(second, text=t('Quais dias você PODE correr? (marque pelo menos a quantidade indicada)')).grid(row=1, column=0, columnspan=3, sticky='w', pady=(15, 5))
        day_frame = ttk.Frame(second)
        day_frame.grid(row=2, column=0, columnspan=3, sticky='w')
        for i, lab in enumerate(WEEKDAY_LABELS):
            ttk.Checkbutton(day_frame, text=t(lab), variable=self.available[i]).grid(row=0, column=i, padx=9)
        _field(second, 3, 'Data mínima para começar', self.start, help_text='AAAA-MM-DD')
        _field(second, 4, 'Data-limite desejada', self.deadline, help_text='AAAA-MM-DD (pode deixar vazio)')
        ttk.Label(second, text=t('O sistema escolhe os dias mais espaçados e sugere um prazo. Se a data-limite for muito cedo, ele avisa e preserva a progressão em vez de acelerar o plano.'), wraplength=670, style="Muted.TLabel").grid(row=5, column=0, columnspan=3, sticky='w', pady=16)

        ttk.Label(third, text=t('Como controlar os treinos?')).grid(row=0, column=0, sticky='w', pady=7)
        cb = ttk.Combobox(third, textvariable=self.method, values=[t(x) for x in METHODS], state='readonly', width=30)
        cb.grid(row=0, column=1, sticky='ew', pady=7)
        cb.bind('<<ComboboxSelected>>', lambda _: self._refresh_method())
        self.hr_label = ttk.Label(third, text=t('FC máxima (bpm)'))
        self.hr_label.grid(row=1, column=0, sticky='w', pady=6)
        self.hr_entry = ttk.Entry(third, textvariable=self.max_hr, width=13)
        self.hr_entry.grid(row=1, column=1, sticky='w', pady=6)
        self.method_info = ttk.Label(third, text=t(''), wraplength=650, style="Muted.TLabel")
        self.method_info.grid(row=2, column=0, columnspan=3, sticky='w', pady=12)
        ttk.Checkbutton(third, text=t('Tive lesão ou desconforto recente que pode limitar os treinos'), variable=self.discomfort).grid(row=3, column=0, columnspan=3, sticky='w', pady=(20, 5))
        ttk.Label(third, text=t('O gerador é educativo e conservador; não faz diagnóstico. Em caso de sintomas ou retorno pós-lesão, procure avaliação profissional antes de seguir o plano.'), wraplength=650, style="Muted.TLabel").grid(row=4, column=0, columnspan=3, sticky='w', pady=12)
        self._refresh_method()
        footer = ttk.Frame(outer)
        footer.pack(fill='x', pady=(12, 0))
        ttk.Button(footer, text=t('Cancelar'), command=self.destroy).pack(side='left')
        ttk.Button(footer, text=t('Gerar plano e visualizar  →'), style='Accent.TButton', command=self.generate).pack(side='right')

    def switch_speed_units(self, _event=None):
        from gerador_plano import pace_to_seconds, fmt_pace
        to_kmh = to_pt(self.speed_units.get()) == 'Velocidade (km/h)'
        self.current_label.configure(text=t('Velocidade atual (km/h)' if to_kmh else 'Pace atual (min/km)'))
        self.target_label.configure(text=t('Velocidade objetivo (km/h)' if to_kmh else 'Pace objetivo (min/km)'))
        for variable in (self.current_pace, self.target_pace):
            try:
                if to_kmh:
                    sec = pace_to_seconds(variable.get())
                    variable.set(f'{3600/sec:.2f}'.replace('.', ','))
                else:
                    kmh = float(variable.get().replace(',', '.'))
                    if kmh > 0:
                        variable.set(fmt_pace(3600/kmh))
            except ValueError:
                pass

    def normalized_pace(self, raw):
        if to_pt(self.speed_units.get()) == 'Pace (min/km)':
            return raw.strip()
        from gerador_plano import fmt_pace
        velocity = float(raw.replace(',', '.'))
        if not 3 <= velocity <= 20:
            raise ValueError('Velocidade precisa ficar entre 3 e 20 km/h.')
        return fmt_pace(3600 / velocity)

    def _refresh_method(self):
        method = to_pt(self.method.get())
        if method == 'FC (%FCmax)':
            self.hr_entry.configure(state='normal')
            self.method_info.configure(text=t('Usa faixas como 65-74% HR. Informe FCmax confiável; não converte bpm exato em etapas, pois a API do Intervals usa % ou zonas.'))
        else:
            self.hr_entry.configure(state='disabled')
            self.method_info.configure(text=t({
                'Pace absoluto':'Usa faixas absolutas como 08:40-08:20/km Pace; não depende do pace limiar salvo no Intervals.icu.',
                'Zona de FC':'Usa Z1 HR, Z2 HR e Z3 HR. Configure e revise suas zonas de FC de corrida no Intervals.icu.',
                'Zona de pace':'Usa Z1 Pace, Z2 Pace e Z3 Pace. Configure e revise suas zonas de pace de corrida no Intervals.icu.',
            }.get(method, '')))

    def _stats_for_plan(self):
        if not self.activity_stats:
            return None
        keep = ('source','analyzed_on','valid_runs_8w','weekly_km_4w','weekly_runs_4w',
                'longest_activity_km_8w','estimated_recent_pace_seconds','median_hr_8w',
                'highest_recorded_hr_8w','median_activity_minutes_8w','latest_run_date')
        return {k:self.activity_stats.get(k) for k in keep}

    def generate(self):
        try:
            req = PlanRequest(
                name=self.name.get().strip(), goal=to_pt(self.goal.get()),
                distance_km=float(self.distance.get().replace(',', '.')),
                longest_km=float(self.longest.get().replace(',', '.')),
                current_pace=self.normalized_pace(self.current_pace.get()), target_pace=self.normalized_pace(self.target_pace.get()) if self.target_pace.get().strip() else '',
                days_per_week=int(self.days.get()),
                available_days=[d for d, checked in enumerate(self.available) if checked.get()],
                start=self.start.get().strip(), deadline=self.deadline.get().strip(),
                method=to_pt(self.method.get()), max_hr=int(self.max_hr.get()) if to_pt(self.method.get()) == 'FC (%FCmax)' else None,
                recent_training=to_pt(self.training.get()), discomfort=self.discomfort.get(),
                activity_stats=self._stats_for_plan())
            plan = generate_plan(req)
        except (ValueError, TypeError) as error:
            messagebox.showerror('Verifique as respostas', str(error), parent=self)
            return
        self.destroy()
        self.on_generate(plan)


class GeneratorTab:
    def __init__(self, app, frame, plans_dir: Path):
        self.app = app
        self.frame = frame
        self.plans_dir = plans_dir
        self.generated = None
        self.loading_activities = False
        self.auto_attempted = False
        self.activity_stats = None
        self.base_generated = None
        self.analysis_label = tk.StringVar(value=t('Sem análise carregada. Clique em “Ler minhas corridas” para personalizar o gerador.'))
        self._build()

    def _build(self):
        f = self.frame
        ttk.Label(f, text=t('Planeje sua próxima conquista'), style='Title.TLabel').pack(anchor='w')
        ttk.Label(f, text=t('O sistema faz perguntas, sugere a duração e monta treinos estruturados para revisar antes de publicar.'), wraplength=920).pack(anchor='w', pady=(4, 9))
        toolbar = ttk.Frame(f)
        toolbar.pack(fill='x', pady=(0, 12))
        ttk.Button(toolbar, text=t('Ler minhas corridas'), style='Accent.TButton', command=self.fetch_activities).pack(side='left', padx=(0, 9))
        ttk.Button(toolbar, text=t('Criar plano'), command=self.open_wizard).pack(side='left', padx=(0, 7))
        ttk.Button(toolbar, text=t('2. Salvar plano no Windows'), command=self.save_generated).pack(side='left', padx=(0, 7))
        ttk.Button(toolbar, text=t('3. Abrir no editor'), command=self.open_editor).pack(side='left', padx=(0, 7))
        ttk.Label(f, textvariable=self.analysis_label, style='Subtitle.TLabel',
                  wraplength=980, justify='left').pack(anchor='w', pady=(0, 11))
        self.chart = tk.Canvas(f, height=94, bg=PANEL, highlightthickness=0)
        self.chart.pack(fill='x', pady=(0, 12))
        self.chart.bind('<Configure>', lambda _: self.draw_chart())
        self.summary = tk.StringVar(value=t('Nenhum plano gerado. Clique em “Criar plano” para começar.'))
        ttk.Label(f, textvariable=self.summary, wraplength=950, font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 8))
        outer = ttk.Panedwindow(f, orient='vertical')
        outer.pack(fill='both', expand=True)
        preview = ttk.Frame(outer)
        bottom = ttk.Frame(outer)
        outer.add(preview, weight=3)
        outer.add(bottom, weight=2)
        cols = ('date','week','phase','name','min')
        self.grid = ttk.Treeview(preview, columns=cols, show='headings', selectmode='browse')
        for key, label, width in [('date','Data',100),('week','Semana',65),('phase','Etapa',105),('name','Treino',540),('min','Min. aprox.',100)]:
            self.grid.heading(key,text=t(label))
            self.grid.column(key,width=width,stretch=(key=='name'))
        scrollbar = ttk.Scrollbar(preview, orient='vertical', command=self.grid.yview)
        self.grid.configure(yscrollcommand=scrollbar.set)
        self.grid.pack(side='left',fill='both',expand=True)
        scrollbar.pack(side='right',fill='y')
        self.grid.bind('<<TreeviewSelect>>', self.show_selected)
        ttk.Label(bottom, text=t('Treino selecionado / Observações')).pack(anchor='w', pady=(5, 3))
        self.description = tk.Text(bottom, height=12, wrap='word', font=('Consolas',10))
        text_box(self.description)
        desc_bar = ttk.Scrollbar(bottom, orient='vertical', command=self.description.yview)
        self.description.configure(yscrollcommand=desc_bar.set, state='disabled')
        self.description.pack(side='left',fill='both',expand=True)
        desc_bar.pack(side='right',fill='y')
        ttk.Label(f, text=t('Não envia automaticamente. Depois de conferir, salve, abra no editor e use “Enviar à API” na aba Planos locais.'), wraplength=940).pack(anchor='w',pady=(9,0))

    def draw_chart(self):
        c = self.chart
        c.delete('all')
        width = max(400, c.winfo_width())
        stats = self.activity_stats
        c.create_text(16, 14, text=t('VOLUME SEMANAL  •  ÚLTIMAS 8 SEMANAS'),
                      fill='#A8BAD0', font=('Segoe UI Semibold', 9), anchor='w')
        if not stats:
            c.create_text(16, 56, text=t('Conecte sua conta para visualizar o histórico de corrida.'),
                          fill='#A8BAD0', font=('Segoe UI', 10), anchor='w')
            return
        weeks = stats['weekly_breakdown']
        high = max(1, max(w['km'] for w in weeks))
        usable = width - 35
        item = usable / 8
        for i, week in enumerate(weeks):
            bar_height = 45 * week['km'] / high
            x = 20 + i*item + 8
            c.create_rectangle(x, 76-bar_height, x+min(42, item-15), 76,
                               fill=ACCENT if i>=4 else '#377A91', outline='')
            c.create_text(x + 17, 85, text=t(f"{week['km']:g}"),
                          fill='#D8E6F6', font=('Segoe UI', 8))

    def fetch_activities(self):
        if self.loading_activities:
            return
        if not self.app.api_key.get().strip():
            messagebox.showinfo('API Key necessária',
                'Vá em Conexão, informe sua API Key e depois volte ao Gerador.')
            return
        self.auto_attempted = True
        self.loading_activities = True
        end = date.today().isoformat()
        start = (date.today()-timedelta(days=84)).isoformat()
        self.app.work('Analisando suas corridas no Intervals.icu...',
                      lambda: analyze_activities(self.app.api().activities(start, end)),
                      self.on_activities_loaded,
                      on_error=lambda: self._finish_loading())

    def _finish_loading(self):
        self.loading_activities = False

    def on_activities_loaded(self, stats):
        self._finish_loading()
        self.activity_stats = stats
        self.draw_chart()
        self.analysis_label.set(t('HISTÓRICO REAL  •  ') + summary_lines(stats, get_language()).replace('\n','    •    '))
        if stats['valid_runs_8w'] < 4:
            messagebox.showwarning('Histórico limitado',
                'Poucas corridas recentes para personalização segura. O sistema seguirá conservador.\n\n'
                + '\n'.join(t(x) for x in stats['warnings'][:2]))
        self.app.status.set(translate_template(f"{stats['valid_runs_8w']} corridas analisadas. Abra ‘Criar plano’ para aplicar o histórico."))

    def relocalize(self):
        self.draw_chart()
        if self.activity_stats:
            self.analysis_label.set(t('HISTÓRICO REAL  •  ') +
                                    summary_lines(self.activity_stats, get_language()).replace('\n', '    •    '))
        else:
            self.analysis_label.set(t('Sem análise carregada. Clique em “Ler minhas corridas” para personalizar o gerador.'))
        if self.base_generated:
            self.show_plan(self.base_generated)
        else:
            self.summary.set(t('Nenhum plano gerado. Clique em “Criar plano” para começar.'))

    def open_wizard(self):
        PlanWizard(self.frame.winfo_toplevel(), self.show_plan, self.activity_stats)

    def _set_text(self, value):
        self.description.configure(state='normal')
        self.description.delete('1.0','end')
        self.description.insert('1.0',value)
        self.description.configure(state='disabled')

    def show_plan(self, plan):
        self.base_generated = plan
        self.generated = localize_plan(plan, get_language())
        events = self.generated['events']
        self.grid.delete(*self.grid.get_children())
        for n, event in enumerate(events):
            self.grid.insert('','end',iid=str(n), values=(event['start_date_local'][:10], event['_week'],event['_phase'],event['name'],event['_estimated_minutes']))
        deadline = self.generated['request'].get('deadline','')
        status = '  |  PRAZO SOLICITADO CURTO' if deadline and self.generated['recommended_end'] > deadline else ''
        self.summary.set(translate_template(f"{self.generated['name']}  |  {len(events)} treinos em {self.generated['recommended_weeks']} semanas  |  Dias: {', '.join(self.generated['chosen_days'])}  |  Previsão: {self.generated['recommended_end']}{status}"))
        self._set_text(t('ORIENTAÇÕES GERAIS DO PLANO (não repetidas em cada treino)\n\n') +
                       '\n\n'.join('• '+note for note in self.generated['warnings']))
        if events:
            self.grid.selection_set('0')
            self.grid.focus('0')
            self.show_selected()
        self.app.status.set(t('Plano calculado localmente. Revise e salve antes de enviar.'))

    def show_selected(self, *_):
        selected = self.grid.selection()
        if selected and self.generated:
            event = self.generated['events'][int(selected[0])]
            structured = event['description'].split('\n\n', 1)[-1]
            self._set_text(t('OBSERVAÇÃO DO TREINO\n') + event.get('_note', '') +
                           t('\n\nESTRUTURA PARA O INTERVALS.ICU\n\n') + structured +
                           translate_template(f"\n\nDistância total aproximada: {event.get('_estimated_km', 0):.1f} km. "
                           'Em FC e zonas, o valor é uma projeção, não uma meta exata.'))

    def save_generated(self):
        if not self.generated:
            messagebox.showinfo('Gerador', 'Gere um plano primeiro.')
            return
        base = filedialog.askdirectory(initialdir=str(self.plans_dir), title=t('Escolha onde salvar a pasta do plano'))
        if not base:
            return
        name = re.sub(r'[^\w-]+','_', self.generated['name'],flags=re.UNICODE).strip('_')[:55] or 'plano_corrida'
        path = Path(base)/name
        if path.exists():
            n=2
            while (Path(base)/f'{name}_{n}').exists():
                n+=1
            path=Path(base)/f'{name}_{n}'
        try:
            path.mkdir(parents=True)
            json_path=path/'plano.json'
            json_path.write_text(json.dumps(self.generated,ensure_ascii=False,indent=2),encoding='utf-8')
            with (path/'treinos.csv').open('w',encoding='utf-8-sig',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=['date','type','name','description'])
                writer.writeheader()
                for e in self.generated['events']:
                    writer.writerow({'date':e['start_date_local'][:10], 'type':'Run','name':e['name'],'description':e['description']})
            txt = (t('PLANO: ')+self.generated['name']+'\n'
                   + t('Duração estimada: ')+f"{self.generated['recommended_weeks']}"+t(' semanas')+'\n'
                   + t('Período: ')+self.generated['planned_start']+t(' até ')+self.generated['recommended_end']+'\n'
                   + t('Dias: ')+', '.join(self.generated['chosen_days'])+'\n\n'
                   + t('ORIENTAÇÕES\n')+'\n'.join('- '+s for s in self.generated['warnings'])+'\n\n'
                   + t('TREINOS\n\n')+'\n\n'.join(e['start_date_local'][:10]+' — '+e['name']+'\n'+e['description'] for e in self.generated['events']))
            (path/'resumo_para_imprimir.txt').write_text(txt,encoding='utf-8')
        except (OSError, ValueError) as ex:
            messagebox.showerror('Salvar plano',str(ex))
            return
        self.generated['_last_saved_path']=str(json_path)
        messagebox.showinfo('Plano salvo',f'Pasta criada:\n{path}\n\nArquivos: plano.json, treinos.csv, resumo_para_imprimir.txt')
        self.app.status.set(t('Plano salvo em: ')+str(path))

    def open_editor(self):
        if not self.generated:
            messagebox.showinfo('Gerador', 'Gere um plano primeiro.')
            return
        json_path = self.generated.get('_last_saved_path')
        self.app.load_generated_plan(self.generated, Path(json_path) if json_path else None)
