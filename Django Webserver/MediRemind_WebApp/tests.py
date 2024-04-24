from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from .models import MedicationSchedule
from django.utils import timezone
from unittest.mock import patch
from .models import Notification, Device, Room, MQTTConfiguration
from .forms import MQTTConfigurationForm, DeviceForm, RoomForm
from .models import Notification, NotificationType

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

class ConfigurationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.url = reverse('configuration')  # Make sure this matches the actual URL name

        # Ensuring that an MQTTConfiguration exists for the user
        MQTTConfiguration.objects.create(user=self.user, broker_address='http://defaultaddress.com', port=1883)

    def test_configuration_view_loads_forms(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['mqtt_form'], MQTTConfigurationForm)
        self.assertIsInstance(response.context['device_form'], DeviceForm)
        self.assertIsInstance(response.context['room_form'], RoomForm)

    def test_post_valid_mqtt_data_redirects(self):
        # Data to update
        post_data = {
            'mqtt_submit': 'Submit',
            'broker_address': 'http://newaddress.com',
            'port': 1884
        }
        response = self.client.post(self.url, post_data)
        self.assertRedirects(response, self.url)  # Checking for the redirect after post

        # Verify that data was updated correctly
        mqtt_config = MQTTConfiguration.objects.get(user=self.user)
        self.assertEqual(mqtt_config.broker_address, 'http://newaddress.com')
        self.assertEqual(mqtt_config.port, 1884)

#python manage.py test MediRemind_WebApp.tests.NotificationAPIViewTests
class NotificationAPIViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        # Create a token for the test user
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.url = reverse('notification_api')

    def test_post_notification(self):
        data = {'message': 'Test Notification', 'type': NotificationType.INFO.name, 'timestamp': timezone.now()}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.first().message, 'Test Notification')

    def test_get_notifications(self):
        Notification.objects.create(user=self.user, message='Test 1', type=NotificationType.INFO.name, timestamp=timezone.now())
        Notification.objects.create(user=self.user, message='Test 2', type=NotificationType.CRITICAL.name, timestamp=timezone.now())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)