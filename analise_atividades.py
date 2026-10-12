"""Leitura e síntese cautelosa de corridas concluídas no Intervals.icu.

Nunca trata distância total de uma atividade como distância contínua sem caminhada.
Nunca transforma FC máxima observada em FC máxima fisiológica.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import date, timedelta
from statistics import median
from typing import Any
import math

RUN_TYPES = {'Run', 'VirtualRun', 'TrailRun', 'Treadmill', 'IndoorRun'}


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def analyze_activities(activities: list[dict[str, Any]], today: date | None = None) -> dict:
    today = today or date.today()
    since = today - timedelta(days=84)
    runs = []
    discarded = 0
    for row in activities:
        if not isinstance(row, dict) or row.get('type') not in RUN_TYPES:
            continue
        try:
            on = date.fromisoformat(str(row.get('start_date_local', ''))[:10])
        except ValueError:
            discarded += 1
            continue
        if not since <= on <= today:
            continue
        dist_m = _number(row.get('distance'))
        seconds = _number(row.get('moving_time'))
        if not dist_m or not seconds or not 300 <= seconds <= 43200 or not 300 <= dist_m <= 100000:
            discarded += 1
            continue
        km = dist_m / 1000
        pace = seconds / km
        if not 180 <= pace <= 1800:
            discarded += 1
            continue
        hr = _number(row.get('average_heartrate'))
        max_observed_hr = _number(row.get('max_heartrate'))
        runs.append({'date': on.isoformat(), 'km': round(km, 3), 'seconds': int(seconds),
                     'pace_seconds': pace, 'hr': round(hr) if hr and 70 <= hr <= 225 else None,
                     'max_observed_hr': round(max_observed_hr) if max_observed_hr and 70 <= max_observed_hr <= 230 else None})
    runs.sort(key=lambda r:r['date'])
    last28 = today - timedelta(days=27)
    last56 = today - timedelta(days=55)
    four = [r for r in runs if r['date'] >= last28.isoformat()]
    eight = [r for r in runs if r['date'] >= last56.isoformat()]
    # Semanas móveis completas relativas a hoje (cada uma com 7 dias).
    weeks = []
    for i in range(7, -1, -1):
        start = today - timedelta(days=7*(i+1)-1)
        end = today - timedelta(days=7*i)
        group = [r for r in runs if start.isoformat() <= r['date'] <= end.isoformat()]
        weeks.append({'start':start.isoformat(), 'end':end.isoformat(), 'km':round(sum(r['km'] for r in group),2), 'runs':len(group)})
    valid_paces = [r['pace_seconds'] for r in eight if r['km'] >= 1 and r['seconds'] >= 600]
    hr_values = [r['hr'] for r in eight if r['hr']]
    observed_max = [r['max_observed_hr'] for r in eight if r['max_observed_hr']]
    total_four = sum(r['km'] for r in four)
    sample_count = len(eight)
    last_date = runs[-1]['date'] if runs else None
    messages = []
    if not runs:
        messages.append('Nenhuma corrida válida encontrada nos últimos 84 dias. Informe seu nível manualmente.')
    elif sample_count < 4:
        messages.append('Histórico insuficiente (menos de 4 corridas em 8 semanas): recomendações pouco confiáveis.')
    if not hr_values:
        messages.append('Sem FC média válida no período. Nenhuma meta de FC será inferida.')
    messages.append('Distância registrada não prova corrida sem caminhar. Confirme sua maior distância contínua no formulário.')
    messages.append('FC máxima registrada em um treino NÃO é sua FCmax real; não será usada como FCmax automaticamente.')
    return {
        'source':'Intervals.icu /activities', 'analyzed_on':today.isoformat(),
        'window_days':84, 'valid_runs_12w':len(runs), 'valid_runs_8w':sample_count,
        'runs_4w':len(four), 'weekly_km_4w':round(total_four/4,2),
        'weekly_km_8w':round(sum(r['km'] for r in eight)/8,2),
        'weekly_runs_4w':round(len(four)/4,2),
        'active_weeks_8w':sum(w['runs']>0 for w in weeks),
        'longest_activity_km_8w':round(max((r['km'] for r in eight), default=0),2),
        'median_activity_km_8w':round(median([r['km'] for r in eight]),2) if eight else None,
        'median_activity_minutes_8w':round(median([r['seconds'] for r in eight])/60,1) if eight else None,
        'estimated_recent_pace_seconds':round(median(valid_paces)) if valid_paces else None,
        'median_hr_8w':round(median(hr_values)) if hr_values else None,
        'highest_recorded_hr_8w':max(observed_max) if observed_max else None,
        'latest_run_date':last_date,
        'weekly_breakdown':weeks,
        'warnings':messages,
        'runs':runs,
    }


def summary_lines(stats: dict, lang: str = 'pt_BR') -> str:
    from gerador_plano import fmt_pace
    pace = stats.get('estimated_recent_pace_seconds')
    if lang == 'en':
        return '\n'.join([
            f"Runs: {stats['valid_runs_8w']} in the last 8 weeks ({stats['runs_4w']} in the last 4)",
            f"Avg. distance: {stats['weekly_km_4w']:.1f} km/week | Frequency: {stats['weekly_runs_4w']:.1f} runs/week",
            f"Longest recorded activity: {stats['longest_activity_km_8w']:.1f} km (may include walking)",
            f"Median pace from valid runs: {fmt_pace(pace) if pace else 'unavailable'} min/km",
            f"Median average HR: {stats['median_hr_8w']} bpm" if stats.get('median_hr_8w') else 'Average HR: insufficient data',
            f"Most recent run: {stats['latest_run_date'] or 'not found'}",
        ])
    return '\n'.join([
        f"Corridas: {stats['valid_runs_8w']} nas últimas 8 semanas ({stats['runs_4w']} nas últimas 4)",
        f"Volume médio: {stats['weekly_km_4w']:.1f} km/semana | Frequência: {stats['weekly_runs_4w']:.1f} corridas/semana",
        f"Maior atividade: {stats['longest_activity_km_8w']:.1f} km (não comprova corrida sem pausas)",
        f"Pace mediano das atividades válidas: {fmt_pace(pace) if pace else 'indisponível'} min/km",
        f"FC média mediana: {stats['median_hr_8w']} bpm" if stats.get('median_hr_8w') else 'FC média: dados insuficientes',
        f"Última corrida: {stats['latest_run_date'] or 'não encontrada'}",
    ])
