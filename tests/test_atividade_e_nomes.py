"""Testes locais sem credenciais, sem rede e sem modificar calendário remoto."""
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analise_atividades import analyze_activities, summary_lines
from gerador_plano import PlanRequest, generate_plan, _session_stats

TODAY = date(2026,10,12)


def fake_run(day_ago, km, pace=480, hr=144, sport='Run'):
    return {'type':sport, 'start_date_local':(TODAY-timedelta(days=day_ago)).isoformat()+'T07:30:00',
            'distance':km*1000, 'moving_time':km*pace,
            'average_heartrate':hr, 'max_heartrate':174}


def req(stats=None, goal='Correr sem parar'):
    return PlanRequest('5 km sem parar',goal,5,2,'08:00','07:30',3,[1,3,5],
                       '2026-10-13','2027-01-31','Zona de FC',activity_stats=stats)

class ActivityTests(unittest.TestCase):
    def setUp(self):
        self.rows=[fake_run(x,2.0+x%3*.3) for x in (0,3,7,11,15,19,22,27,35,41,48,54)]

    def test_recent_metrics_are_computed_from_records(self):
        result=analyze_activities(self.rows,today=TODAY)
        self.assertEqual(result['valid_runs_8w'],len(self.rows))
        self.assertGreater(result['weekly_km_4w'],1)
        self.assertEqual(result['median_hr_8w'],144)
        self.assertEqual(result['highest_recorded_hr_8w'],174)
        self.assertEqual(len(result['weekly_breakdown']),8)
        self.assertIn('não comprova',summary_lines(result))

    def test_not_count_bike_or_walk(self):
        result=analyze_activities(self.rows+[fake_run(1,40,sport='Ride'),fake_run(2,3,sport='Walk')],today=TODAY)
        self.assertEqual(result['valid_runs_8w'],len(self.rows))

    def test_missing_hr_never_infers_max_hr(self):
        rows=[fake_run(1,3,hr=None)]
        result=analyze_activities(rows,today=TODAY)
        self.assertIsNone(result['median_hr_8w'])
        self.assertIsNotNone(result['highest_recorded_hr_8w'])
        self.assertTrue(any('FC máxima' in x for x in result['warnings']))

    def test_future_and_bad_data_excluded(self):
        rows=[fake_run(-1,3),fake_run(2,0.05),fake_run(2,2)]
        self.assertEqual(analyze_activities(rows,today=TODAY)['valid_runs_8w'],1)

    def test_empty_history_gracefully_falls_back(self):
        x=analyze_activities([],today=TODAY)
        self.assertIsNone(x['estimated_recent_pace_seconds'])
        self.assertEqual(x['valid_runs_8w'],0)

    def test_api_data_changes_recommended_duration(self):
        stats=analyze_activities(self.rows,today=TODAY)
        slow_stats={k:v for k,v in stats.items() if k not in ('runs','weekly_breakdown','warnings')}
        slow_stats['weekly_km_4w']=2
        slow_stats['weekly_runs_4w']=1
        basic=generate_plan(req())
        personalized=generate_plan(req(slow_stats))
        self.assertGreater(personalized['recommended_weeks'],basic['recommended_weeks'])
        self.assertLessEqual(personalized['events'][0]['_estimated_minutes'],basic['events'][0]['_estimated_minutes'])

    def test_title_has_week_distance_time_and_kind(self):
        plan=generate_plan(req())
        for e in plan['events']:
            self.assertRegex(e['name'],r'^S\d+-\d+,\d+km/\d+min - (Longão|Fartlek|Intervalado|Regenerativo|Rodagem leve|Teste|Corrida/caminhada)$')
            self.assertLessEqual(len(e['_note']),120)
            self.assertTrue(e['description'].startswith('Dica: '))
            self.assertIn('Warmup',e['description'])
        self.assertEqual(plan['events'][-1]['_kind'],'Teste')

    def test_speed_goals_have_fartlek_and_intervals(self):
        plan=generate_plan(req(goal='Melhorar velocidade'))
        kinds={e['_kind'] for e in plan['events']}
        self.assertIn('Fartlek',kinds)
        self.assertIn('Intervalado',kinds)
        self.assertIn('Longão',kinds)

    def test_reps_time_includes_recovery(self):
        workout='Warmup\n- 10m Z1 HR intensity=warmup\n\n3x\n- 2m Z3 HR intensity=interval\n- 90s Z1 HR intensity=recovery\n\nCooldown\n- 5m Z1 HR intensity=cooldown'
        km, mins=_session_stats(workout,480,450)
        self.assertEqual(mins,26)  # 10 + 3*(2 + 1.5) + 5 = 25.5 min
        self.assertGreater(km,1)

if __name__=='__main__':
    unittest.main()
