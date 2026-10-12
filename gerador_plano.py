"""Gerador deterministico e revisavel de planos para iniciantes de corrida.

Nao substitui treinador nem avaliacao clinica. Sem dependencia de internet.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import date, timedelta
from itertools import combinations
import math
import re
from typing import Optional

WEEKDAY_LABELS = ('Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom')
METHODS = ('Pace absoluto', 'FC (%FCmax)', 'Zona de FC', 'Zona de pace')
GOALS = ('Correr sem parar', 'Melhorar velocidade')


def pace_to_seconds(value: str) -> int:
    text = value.strip()
    match = re.fullmatch(r'(\d{1,2}):(\d{2})', text)
    if not match or int(match.group(2)) > 59:
        raise ValueError('Digite pace no formato MM:SS, por exemplo 08:00.')
    seconds = int(match.group(1)) * 60 + int(match.group(2))
    if not 180 <= seconds <= 1200:
        raise ValueError('Informe um pace plausível entre 03:00 e 20:00 min/km.')
    return seconds


def fmt_pace(seconds: int) -> str:
    seconds = int(round(seconds))
    return f'{seconds // 60}:{seconds % 60:02d}'


def pace_range(a: float, b: float) -> str:
    slower = fmt_pace(max(a, b))
    faster = fmt_pace(min(a, b))
    return f'{slower}-{faster}/km Pace'


def minute_string(value: float) -> str:
    seconds = max(30, int(round(value * 60 / 30) * 30))
    minutes, sec = divmod(seconds, 60)
    return f'{minutes}m' if not sec else f'{minutes}m{sec}s' if minutes else f'{sec}s'


@dataclass
class PlanRequest:
    name: str
    goal: str
    distance_km: float
    longest_km: float
    current_pace: str
    target_pace: str
    days_per_week: int
    available_days: list[int]
    start: str
    deadline: str
    method: str
    max_hr: Optional[int] = None
    recent_training: str = 'Regular (1-3 meses)'
    discomfort: bool = False
    activity_stats: Optional[dict] = None

    def validate(self) -> None:
        if not (2 <= len(self.name.strip()) <= 90):
            raise ValueError('O nome deve ter entre 2 e 90 caracteres.')
        if self.goal not in GOALS or self.method not in METHODS:
            raise ValueError('Selecione um objetivo e método de intensidade válidos.')
        if not 2 <= self.distance_km <= 10:
            raise ValueError('A distância objetivo precisa ficar entre 2 e 10 km.')
        if not 0 <= self.longest_km <= 100:
            raise ValueError('Informe uma distância atual válida (0 a 100 km).')
        if not 2 <= self.days_per_week <= 5:
            raise ValueError('Escolha entre 2 e 5 treinos por semana.')
        if len(set(self.available_days)) < self.days_per_week:
            raise ValueError('Marque pelo menos tantos dias disponíveis quanto os treinos semanais.')
        if any(d not in range(7) for d in self.available_days):
            raise ValueError('Dias da semana inválidos.')
        if self.method == 'FC (%FCmax)' and (self.max_hr is None or not 100 <= self.max_hr <= 230):
            raise ValueError('Para FC, informe FC máxima medida ou estimada conscientemente, entre 100 e 230 bpm.')
        start = date.fromisoformat(self.start)
        if start < date.today():
            raise ValueError('A data inicial não pode estar no passado.')
        if self.deadline and date.fromisoformat(self.deadline) < start:
            raise ValueError('A data limite não pode ser anterior ao início.')
        current = pace_to_seconds(self.current_pace)
        if self.goal == 'Melhorar velocidade':
            target = pace_to_seconds(self.target_pace)
            if target >= current:
                raise ValueError('Para ganhar velocidade, o pace objetivo deve ser MENOR que o atual (ex.: 07:30 é mais rápido que 08:00).')
        elif self.target_pace.strip():
            pace_to_seconds(self.target_pace)


def recommend_weeks(req: PlanRequest) -> int:
    if req.goal == 'Correr sem parar':
        if req.longest_km >= req.distance_km:
            weeks = 5
        else:
            # Aumenta o prazo se ainda nao existe base continua de corrida.
            weeks = max(6, min(18, math.ceil(5 + 2.0 * (req.distance_km - req.longest_km))))
            if req.longest_km < 0.5:
                weeks = max(weeks, 10)
    else:
        current, target = pace_to_seconds(req.current_pace), pace_to_seconds(req.target_pace)
        improvement = (current - target) / current
        weeks = 10 if improvement <= .05 else 12 if improvement <= .1 else 16 if improvement <= .16 else 20
        if req.longest_km < req.distance_km * 0.8:
            weeks += 4
    if req.days_per_week == 2:
        weeks += 2
    if req.recent_training == 'Iniciante / parado':
        weeks += 2
    if req.discomfort:
        weeks += 2
    stats = req.activity_stats or {}
    if stats and stats.get('valid_runs_8w', 0) >= 3:
        # Volume e frequencia reais afetam a estimativa de prazo, sem fingir
        # que conhecemos a distancia percorrida sem paradas.
        if stats.get('weekly_km_4w', 0) < 4:
            weeks += 3
        elif stats.get('weekly_km_4w', 0) < 8:
            weeks += 1
        if stats.get('weekly_runs_4w', 0) + 1 < req.days_per_week:
            weeks += 2
    return min(30, weeks)


def choose_days(available: list[int], count: int) -> tuple[int, ...]:
    """Escolhe a distribuicao com intervalos de descanso mais regulares."""
    if len(available) == count:
        return tuple(sorted(available))
    best = None
    best_key = None
    for seq in combinations(sorted(set(available)), count):
        gaps = [(seq[(i + 1) % len(seq)] - seq[i]) % 7 for i in range(len(seq))]
        # Maximize o menor descanso, depois a regularidade do intervalo.
        key = (min(gaps), -sum((g - 7/count)**2 for g in gaps), tuple(-x for x in seq))
        if best_key is None or key > best_key:
            best, best_key = seq, key
    return best


def first_week_monday(start: date, selected: tuple[int, ...]) -> date:
    monday = start - timedelta(days=start.weekday())
    # Evita uma primeira semana parcial: no maximo 7 dias de espera.
    if min(selected) < start.weekday():
        monday += timedelta(days=7)
    return monday


def intensity(req: PlanRequest, current_sec: int, goal_sec: int, progress: float) -> dict:
    if req.method == 'Zona de FC':
        return {'warm':'Z1 HR', 'easy':'Z2 HR', 'steady':'Z2 HR', 'fast':'Z3 HR', 'recover':'Z1 HR'}
    if req.method == 'Zona de pace':
        return {'warm':'Z1 Pace', 'easy':'Z2 Pace', 'steady':'Z2 Pace', 'fast':'Z3 Pace', 'recover':'Z1 Pace'}
    if req.method == 'FC (%FCmax)':
        return {'warm':'55-65% HR', 'easy':'65-74% HR', 'steady':'70-78% HR', 'fast':'78-86% HR', 'recover':'55-65% HR'}
    # Ranges intencionalmente largas (referencias aproximadas, nao teste fisiologico).
    # Treinos de velocidade aproximam-se do objetivo apenas nas ultimas semanas.
    interval_sec = current_sec + (goal_sec - current_sec) * min(.95, .15 + .8 * progress)
    return {
        'warm': pace_range(current_sec * 1.23, current_sec * 1.34),
        'easy': pace_range(current_sec * 1.13, current_sec * 1.25),
        'steady': pace_range(current_sec * 1.06, current_sec * 1.16),
        'fast': pace_range(interval_sec * 1.03, interval_sec * .98),
        'recover': pace_range(current_sec * 1.25, current_sec * 1.42),
    }


def step(duration: str, target: str, label: str) -> str:
    return f'- {duration} {target} intensity={label}'


def runwalk(run_minutes: float, block_minutes: float, tags: dict, title: str) -> str:
    """Gera etapas de corrida/caminhada; nao mistura controle de FC e pace."""
    parts = ['Warmup', step('6m', tags['warm'], 'warmup'), '', title]
    if run_minutes <= block_minutes + .25:
        parts.append(step(minute_string(run_minutes), tags['easy'], 'active'))
    else:
        block = max(1.0, round(block_minutes * 2) / 2)
        repeat = min(14, int(run_minutes // block))
        remaining = run_minutes - block * repeat
        if repeat >= 2:
            parts.extend([f'{repeat}x', step(minute_string(block), tags['easy'], 'active'), step('90s', tags['recover'], 'recovery')])
        elif repeat == 1:
            parts.extend([step(minute_string(block), tags['easy'], 'active'), step('90s', tags['recover'], 'recovery')])
        if remaining >= .5:
            parts.append(step(minute_string(remaining), tags['easy'], 'active'))
    parts.extend(['', 'Cooldown', step('5m', tags['warm'], 'cooldown')])
    return '\n'.join(parts)


def continuous(minutes: float, tags: dict, title='Corrida leve', distance_km: Optional[float] = None) -> str:
    unit = f'{distance_km:g}km' if distance_km is not None else minute_string(minutes)
    return '\n'.join(['Warmup', step('6m', tags['warm'], 'warmup'), '', title,
                      step(unit, tags['easy'], 'active'), '', 'Cooldown', step('5m', tags['warm'], 'cooldown')])


def quality_session(week: int, n_weeks: int, tags: dict, req: PlanRequest) -> tuple[str, float]:
    if week <= 2 or req.discomfort or req.longest_km < req.distance_km * .8 and week <= 4:
        return continuous(22 + min(12, week * 2), tags), 33 + min(12, week * 2)
    reps = min(6, 3 + week // 3)
    fast_mins = 1 if week <= 5 else 2 if week <= 9 else 3 if week <= 14 else 4
    if week >= n_weeks - 1:
        reps = min(reps, 3)
        fast_mins = 1
    recover = max(2, fast_mins)
    desc = '\n'.join(['Warmup', step('10m', tags['warm'], 'warmup'), '', 'Blocos controlados',
                      f'{reps}x', step(minute_string(fast_mins), tags['fast'], 'interval'),
                      step(minute_string(recover), tags['recover'], 'recovery'), '',
                      'Cooldown', step('8m', tags['warm'], 'cooldown')])
    return desc, 18 + reps * (fast_mins + recover)



def _session_stats(description: str, pace_seconds: int, target_seconds: int) -> tuple[float,int]:
    """Estima km e soma duracoes dos passos que NOS mesmos geramos.

    Nas sessoes por FC/zona os km sao necessariamente aproximados.
    Repeticoes seguem apenas o formato Nx + duas linhas usado neste gerador.
    """
    lines = description.splitlines()
    distance_m = 0.0
    duration_s = 0.0
    i = 0
    while i < len(lines):
        raw = lines[i].strip()
        repeat = re.fullmatch(r'(\d+)x', raw)
        if repeat:
            count = int(repeat.group(1))
            segments = []
            for child in lines[i+1:i+3]:
                if child.lstrip().startswith('- '):
                    segments.append(child)
            for child in segments:
                secs, meters = _segment_stats(child, pace_seconds, target_seconds)
                duration_s += secs * count
                distance_m += meters * count
            i += 1 + len(segments)
            continue
        if raw.startswith('- '):
            secs, meters = _segment_stats(raw, pace_seconds, target_seconds)
            duration_s += secs
            distance_m += meters
        i += 1
    return (round(distance_m/1000, 2), int(round(duration_s/60)))


def _segment_stats(text: str, pace_seconds: int, target_seconds: int) -> tuple[float, float]:
    match = re.match(r'^-\s+(\d+(?:[.,]\d+)?)(km|m|s)(?:(\d+)s)?(?:\s|$)', text.strip())
    if not match:
        return 0, 0
    value, unit = float(match.group(1).replace(',', '.')), match.group(2)
    if unit == 'km':
        secs, meters = 0, value*1000
    else:
        secs = value*60 if unit == 'm' else value
        if match.group(3):
            secs += int(match.group(3))
        meters = 0
    if 'intensity=interval' in text:
        estimated_pace = max(180, min(pace_seconds, target_seconds * 1.07))
    elif 'intensity=recovery' in text:
        estimated_pace = pace_seconds * 1.44
    elif 'intensity=warmup' in text or 'intensity=cooldown' in text:
        estimated_pace = pace_seconds * 1.32
    else:
        estimated_pace = pace_seconds * 1.16
    # Para pace absoluto, tentar usar a faixa exata da etapa quando presente.
    match_pace = re.search(r'(\d{1,2}:\d{2})-(\d{1,2}:\d{2})/km Pace', text)
    if match_pace:
        estimated_pace = (pace_to_seconds(match_pace.group(1)) + pace_to_seconds(match_pace.group(2)))/2
    if meters:
        secs = meters/1000*estimated_pace
    else:
        meters = secs/estimated_pace*1000
    return secs, meters


def _type_note(workout_type: str, week: int) -> str:
    if workout_type == 'Longão':
        return 'Corra em ritmo confortável, conseguindo conversar. Priorize terminar bem.'
    if workout_type == 'Fartlek':
        return 'Alterne trechos vivos e leves sem sprintar; recupere o fôlego.'
    if workout_type == 'Intervalado':
        return 'Faça os blocos com controle. Desacelere se não recuperar bem.'
    if workout_type == 'Teste':
        return 'Comece conservador e tente manter um ritmo estável até o fim.'
    if workout_type == 'Corrida/caminhada':
        return 'Intercale corrida leve e caminhada; mantenha a respiração confortável.'
    if workout_type == 'Regenerativo':
        return 'Rode bem leve. Hoje o foco é recuperar, não ganhar velocidade.'
    return 'Rode leve e solto, em ritmo de conversa; hidrate-se e recupere bem.'

def generate_plan(req: PlanRequest) -> dict:
    req.validate()
    weeks = recommend_weeks(req)
    days = choose_days(req.available_days, req.days_per_week)
    first = first_week_monday(date.fromisoformat(req.start), days)
    last = first + timedelta(days=7 * (weeks - 1) + max(days))
    current_sec = pace_to_seconds(req.current_pace)
    target_sec = pace_to_seconds(req.target_pace) if req.target_pace else current_sec
    nominal_goal_minutes = req.distance_km * current_sec / 60
    notes = ['Plano estimado por regras conservadoras; não garante desempenho nem substitui avaliação de treinador.',
             'Inclui aquecimento e desaquecimento; intensidade leve significa conseguir conversar.',
             'Se não concluir uma semana com conforto, repita-a antes de progredir. Dor persistente: interrompa o treino e busque avaliação.']
    if req.method in ('Zona de FC', 'Zona de pace'):
        notes.append('Verifique as zonas da modalidade Run no Intervals.icu; Z1/Z2/Z3 dependem do perfil e não são calculadas aqui.')
    elif req.method == 'FC (%FCmax)':
        notes.append(f'FC: metas como percentuais de FCmax (informada: {req.max_hr} bpm). %FCmax não é %FC de limiar; confirme as configurações do Intervals.icu.')
    else:
        notes.append('Paces são estimativas baseadas no pace informado, não um teste de limiar. Em calor/subidas, priorize esforço confortável.')
    if req.discomfort:
        notes.append('Como foi assinalado desconforto/lesão recente, o plano evita sessões intensas e adiciona semanas. Procure orientação antes de retomar se houver sintomas.')
    if req.days_per_week >= 4 and req.longest_km < 3:
        notes.append('Quatro ou cinco sessões podem ser demais para alguns iniciantes. Considere começar com 3 sessões e manter dias extras opcionais.')
    gaps = [((days[(i+1) % len(days)] - days[i]) % 7) for i in range(len(days))]
    if min(gaps) == 1:
        notes.append('Há sessões em dias consecutivos devido à disponibilidade. Mantenha-as fáceis; tente separar corridas por um dia de descanso.')
    stats = req.activity_stats or {}
    if stats:
        notes.append(f"Histórico API: {stats.get('valid_runs_8w', 0)} corridas em 8 semanas; "
                     f"{stats.get('weekly_km_4w', 0)} km/semana e "
                     f"{stats.get('weekly_runs_4w', 0)} sessões/semana nas últimas 4 semanas.")
        if stats.get('median_hr_8w'):
            notes.append(f"FC média mediana observada: {stats['median_hr_8w']} bpm. Não usada como FCmax nem limiar.")
        if stats.get('valid_runs_8w', 0) < 4:
            notes.append('Poucas corridas recentes: mantenha informações manuais e interprete o prazo com cautela.')
    if req.goal == 'Melhorar velocidade' and req.longest_km < req.distance_km * .8:
        notes.append('Sua corrida contínua atual é menor que a distância-alvo. O plano prioriza adaptação antes dos blocos rápidos.')
    if req.deadline:
        limit = date.fromisoformat(req.deadline)
        if last > limit:
            notes.insert(0, f'PRAZO ALERTA: data-limite {limit:%d/%m/%Y} é anterior à previsão {last:%d/%m/%Y}. O sistema NÃO acelera a carga para encaixar no prazo.')
        else:
            notes.append(f'Data-limite {limit:%d/%m/%Y}: a projeção encerra antes desse prazo. A evolução individual pode exigir mais tempo.')
    events = []
    initial_run_minutes = max(2.0, min(req.longest_km * current_sec / 60, nominal_goal_minutes * .92))
    if req.longest_km < .5:
        initial_run_minutes = 7
    initial_run_minutes = min(initial_run_minutes, nominal_goal_minutes)
    stats_recent = req.activity_stats or {}
    if stats_recent.get('valid_runs_8w', 0) >= 3:
        measured_volume = float(stats_recent.get('weekly_km_4w') or 0)
        if measured_volume > 0:
            # Inicio cauteloso orientado pelo volume realmente registrado.
            # Se o histórico é baixo, não presumimos base aeróbica inexistente.
            affordable_minutes = measured_volume / req.days_per_week * current_sec / 60 * 1.10
            initial_run_minutes = min(initial_run_minutes, max(4, affordable_minutes))
            if measured_volume < 3:
                notes.append('Volume recente muito baixo: as primeiras sessões devem ser feitas com pausas de caminhada; dias extras podem ser opcionais.')
    base_long_speed = max(18.0, min(65.0, req.longest_km * current_sec / 60 * .95 + 6))
    if stats_recent.get('valid_runs_8w', 0) >= 3 and stats_recent.get('median_activity_minutes_8w'):
        base_long_speed = min(base_long_speed, max(14, stats_recent['median_activity_minutes_8w'] * 1.05))
    for w in range(weeks):
        week_num = w+1
        p = w / max(1, weeks-1)
        tags = intensity(req, current_sec, target_sec, p)
        # Semana de recuperacao a cada 4 semanas, exceto na ultima (teste).
        deload = (week_num % 4 == 0 and week_num != weeks)
        phase = ('Adaptação' if p < .22 else 'Construção' if p < .72 else 'Consolidação' if p < .92 else 'Objetivo')
        for idx, weekday in enumerate(days):
            on = first + timedelta(days=w*7 + weekday)
            is_long = idx == len(days)-1
            if req.goal == 'Correr sem parar':
                progressive = initial_run_minutes + (nominal_goal_minutes - initial_run_minutes) * p
                if deload:
                    progressive *= .87
                if is_long:
                    session_min = round(max(5, progressive))
                    if w == weeks-1:
                        desc = continuous(nominal_goal_minutes, tags, 'Teste de distância contínua', req.distance_km)
                        kind = 'Teste'
                        estimate = round(nominal_goal_minutes + 11)
                    elif req.longest_km >= 1.5 or p >= .82:
                        desc = continuous(session_min, tags, 'Corrida contínua principal')
                        kind = 'Longão'
                        estimate = session_min + 11
                    else:
                        block = max(1, initial_run_minutes / 3 + (session_min - initial_run_minutes/3)*max(0,p-.15)**1.3)
                        desc = runwalk(session_min, block, tags, 'Corrida / caminhada')
                        kind = 'Corrida/caminhada'
                        estimate = session_min + 11 + 1.5 * max(0, math.ceil(session_min / max(block, 1))-1)
                else:
                    session_min = round(max(5, min(progressive * (.58 if idx == 0 else .72), 36)))
                    if req.longest_km >= 1.5 or p >= .78:
                        desc = continuous(session_min, tags)
                        kind = 'Rodagem leve' if not deload else 'Regenerativo'
                        estimate = session_min + 11
                    else:
                        block = max(1, initial_run_minutes/4 + p*11)
                        desc = runwalk(session_min, block, tags, 'Intervalos fáceis')
                        kind = 'Corrida/caminhada'
                        estimate = session_min + 11 + 1.5 * max(0, math.ceil(session_min/max(block,1))-1)
            else:
                if is_long:
                    main_min = min(80, base_long_speed * (1 + .35*p))
                    if deload:
                        main_min *= .87
                    if w == weeks-1:
                        desc = '\n'.join(['Warmup', step('10m', tags['warm'], 'warmup'), '', 'Teste de pace',
                                          step(f'{req.distance_km:g}km', tags['fast'], 'active'), '',
                                          'Cooldown', step('8m', tags['warm'], 'cooldown')])
                        kind = 'Teste'
                        estimate = round(18 + req.distance_km * target_sec / 60)
                    else:
                        desc = continuous(main_min, tags, 'Rodagem de resistência')
                        kind = 'Longão'
                        estimate = round(main_min + 11)
                elif idx == 1 or (len(days) == 2 and idx == 0):
                    desc, estimate = quality_session(week_num, weeks, tags, req)
                    kind = ('Fartlek' if week_num % 2 else 'Intervalado') if week_num > 2 and not req.discomfort and not (req.longest_km < req.distance_km*.8 and week_num <= 4) else 'Rodagem leve'
                    if kind == 'Fartlek':
                        # Mesmo formato estruturado (tiros leves com recuperação),
                        # mas percebidos como alternância de ritmos sem máxima intensidade.
                        desc = desc.replace('Blocos controlados', 'Fartlek controlado')
                else:
                    main_min = (22 + min(18, 2*week_num)) * (.9 if deload else 1)
                    desc = continuous(main_min, tags, 'Corrida fácil')
                    kind = 'Regenerativo' if deload else 'Rodagem leve'
                    estimate = round(main_min + 11)
            km_approx, minutes_total = _session_stats(desc, current_sec, target_sec)
            # Distância/tempo calculados das etapas, não apenas do bloco principal.
            # O km é aproximado por usar o pace recente como referência nas zonas/FC.
            km_text = f'{km_approx:.1f}'.replace('.', ',')
            title = f'S{week_num}-{km_text}km/{minutes_total}min - {kind}'
            tip = _type_note(kind, week_num)
            # A nota curta vai antes da estrutura, que continua editável no Intervals.icu.
            desc = f'Dica: {tip}\n\n{desc}'
            event = {'category': 'WORKOUT', 'start_date_local': on.isoformat()+'T07:00:00',
                     'type': 'Run', 'name': title,
                     'description': desc, '_week': week_num, '_phase': phase,
                     '_note': tip, '_kind':kind, '_estimated_km':km_approx,
                     '_estimated_minutes': minutes_total}
            events.append(event)
    return {
        'format':'intervals-manager-generated-v3', 'name':req.name,
        'request':asdict(req), 'recommended_weeks':weeks,
        'recommended_end':last.isoformat(), 'planned_start':min(e['start_date_local'][:10] for e in events),
        'chosen_days':[WEEKDAY_LABELS[d] for d in days],
        'warnings':notes, 'events':events,
    }
