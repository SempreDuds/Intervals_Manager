import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gerador_plano import PlanRequest, generate_plan, pace_to_seconds, METHODS, GOALS, choose_days


def request(**overrides):
    obj = dict(name='Teste', goal=GOALS[0], distance_km=5, longest_km=2,
               current_pace='08:00', target_pace='07:30', days_per_week=3,
               available_days=[1,3,5], start=(date.today()+timedelta(days=1)).isoformat(),
               deadline='', method='Zona de FC', max_hr=None, recent_training='Regular (1-3 meses)',
               discomfort=False)
    obj.update(overrides)
    return PlanRequest(**obj)

class EngineTests(unittest.TestCase):
    def test_each_goal_and_target_mode(self):
        for method in METHODS:
            for goal in GOALS:
                with self.subTest(method=method,goal=goal):
                    plan=generate_plan(request(method=method, goal=goal, max_hr=185, longest_km=5 if goal==GOALS[1] else 2))
                    events=plan['events']
                    self.assertEqual(len(events), plan['recommended_weeks']*3)
                    self.assertTrue(all(e['type']=='Run' and e['category']=='WORKOUT' for e in events))
                    self.assertEqual(len({e['start_date_local'] for e in events}), len(events))
                    self.assertTrue(all(e['description'].count('Warmup') == 1 and e['description'].count('Cooldown') == 1 for e in events))
                    if method=='Zona de FC':
                        self.assertTrue(all(' HR' in e['description'] and ' Pace' not in e['description'] for e in events))
                    if method=='Zona de pace':
                        self.assertTrue(all(' Pace' in e['description'] and ' HR' not in e['description'] for e in events))
                    if method=='Pace absoluto':
                        self.assertTrue(all('/km Pace' in e['description'] for e in events))
                    if method=='FC (%FCmax)':
                        self.assertTrue(all('% HR' in e['description'] for e in events))
                    self.assertEqual(events[-1]['start_date_local'][:10], plan['recommended_end'])

    def test_negative_goal_speed_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_plan(request(goal='Melhorar velocidade',target_pace='08:30'))

    def test_warnings_for_short_deadline(self):
        plan=generate_plan(request(deadline=(date.today()+timedelta(days=14)).isoformat()))
        self.assertTrue(any('PRAZO ALERTA' in s for s in plan['warnings']))

    def test_hr_requires_maximum(self):
        with self.assertRaises(ValueError):
            generate_plan(request(method='FC (%FCmax)'))

    def test_beginner_generates_run_walk_and_finishes_distance(self):
        plan=generate_plan(request(longest_km=0, recent_training='Iniciante / parado', method='Zona de pace'))
        self.assertTrue(any('90s' in e['description'] for e in plan['events'][:9]))
        self.assertIn('- 5km Z2 Pace', plan['events'][-1]['description'])

    def test_choose_days_even_spacing(self):
        self.assertEqual(choose_days([0,1,2,3,4,5,6],3), (0,2,4))

    def test_run_days_requested(self):
        plan=generate_plan(request(days_per_week=2, available_days=[1,5]))
        self.assertEqual({date.fromisoformat(e['start_date_local'][:10]).weekday() for e in plan['events']}, {1,5})

    def test_invalid_pace(self):
        for p in ['8','8:7','08:88','00:00','25:00']:
            with self.subTest(p=p), self.assertRaises(ValueError):
                pace_to_seconds(p)

    def test_invalid_distance(self):
        with self.assertRaises(ValueError):
            generate_plan(request(distance_km=21.1))

if __name__=='__main__':
    unittest.main()
