from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import MedicationSchedule
from django.utils import timezone

#python manage.py test

class HomeViewTest(TestCase):
    '''This test checks if the HomeView is accessible by an authenticated user and verifies that the correct context data is available'''
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_home_view_status_code(self):
        response = self.client.get(reverse('profile_home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_context_data(self):
        response = self.client.get(reverse('profile_home'))
        self.assertIn('notifications', response.context)
        self.assertIn('schedules', response.context)

class MedicationScheduleViewTests(TestCase):
    def setUp(self):
        # Set up a user and log in
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # Create medication schedules for the user
        MedicationSchedule.objects.create(
            user=self.user, medication_name="Med1", reminder_time="08:00:00", time_window=1, dosage="100 mg")

    def test_view_schedules(self):
        response = self.client.get(reverse('medication_schedule'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['schedules']), 1)
        self.assertContains(response, "Med1")

    def test_add_schedule(self):
        response = self.client.post(reverse('medication_schedule'), {
            'medication_name': 'Med2',
            'reminder_time': '09:00:00',
            'time_window': 1,
            'dosage': '200 mg'
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect after save
        self.assertEqual(MedicationSchedule.objects.count(), 2)

    def test_invalid_form_submission(self):
        response = self.client.post(reverse('medication_schedule'), {
            'medication_name': '',  # Invalid data
            'reminder_time': 'badtime',  # Invalid time
            'dosage': '200 mg'
        })
        self.assertEqual(response.status_code, 200)  # Stays on the same page
        self.assertEqual(MedicationSchedule.objects.count(), 1)  # No new schedule should be created

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(reverse('medication_schedule'))
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(response.url.startswith('/login'))

