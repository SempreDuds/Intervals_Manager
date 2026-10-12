"""Localization checks. No credentials/network and no graphical display required."""
import unittest
from datetime import date, timedelta
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from i18n import LANGUAGES, t, to_pt, set_language, localize_plan, translate_guidance
from gerador_plano import PlanRequest, GOALS, METHODS, generate_plan
from analise_atividades import summary_lines


class I18nTests(unittest.TestCase):
    def tearDown(self):
        set_language('pt_BR')

    def sample(self, goal='Correr sem parar', method='Zona de FC'):
        return generate_plan(PlanRequest(
            name='Training sample', goal=goal, distance_km=5,
            longest_km=2, current_pace='08:00', target_pace='07:00',
            days_per_week=3, available_days=[1, 3, 5],
            start=(date.today() + timedelta(days=1)).isoformat(),
            deadline=(date.today() + timedelta(days=14)).isoformat(),
            method=method, max_hr=180, recent_training='Regular (1-3 meses)',
        ))

    def test_english_and_portuguese_ui(self):
        set_language('pt_BR')
        self.assertEqual(t('Calendário e exclusão em massa'), 'Calendário e exclusão em massa')
        set_language('en')
        self.assertEqual(t('Calendário e exclusão em massa'), 'Calendar and bulk deletion')
        self.assertEqual(t('Longão'), 'Long run')
        self.assertEqual(to_pt(t('Melhorar velocidade')), 'Melhorar velocidade')
        set_language('pt_BR')
        self.assertEqual(t('Calendar and bulk deletion'), 'Calendário e exclusão em massa')

    def test_workouts_keep_technical_syntax_in_both_languages(self):
        for method in METHODS:
            plan = self.sample(method=method, goal=GOALS[1])
            english = localize_plan(plan, 'en')
            portuguese = localize_plan(plan, 'pt_BR')
            self.assertEqual(len(english['events']), len(portuguese['events']))
            for en, pt in zip(english['events'], portuguese['events']):
                self.assertEqual(en['start_date_local'], pt['start_date_local'])
                self.assertEqual(en['_estimated_minutes'], pt['_estimated_minutes'])
                self.assertEqual(en['_estimated_km'], pt['_estimated_km'])
                self.assertIn('Warmup', en['description'])
                self.assertIn('Cooldown', en['description'])
                self.assertIn('intensity=', en['description'])
                self.assertTrue(en['description'].startswith('Tip: '))
                self.assertTrue(pt['description'].startswith('Dica: '))
                self.assertNotEqual(en['_note'], pt['_note'])
                self.assertIn(' - ', en['name'])
                self.assertIn(' - ', pt['name'])
                self.assertEqual(pt['name'], plan['events'][english['events'].index(en)]['name'])

    def test_guidance_translated_including_deadline(self):
        en = localize_plan(self.sample(), 'en')
        self.assertTrue(any('DEADLINE WARNING' in s for s in en['warnings']))
        self.assertTrue(all('Plano estimado' not in s and 'Data-limite' not in s for s in en['warnings']))
        self.assertEqual(en['chosen_days'], ['Tue', 'Thu', 'Sat'])

    def test_no_auto_conversion_of_user_input(self):
        assert t('My special plan') == 'My special plan'
        assert t('Intervals.icu') == 'Intervals.icu'


if __name__ == '__main__':
    unittest.main()
