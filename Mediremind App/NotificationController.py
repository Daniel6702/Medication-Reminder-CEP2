import smtplib
from EventSystem import EventType, event_system
import uuid
from datetime import datetime
from Database.Models import Notification, NotificationType

class NotificationController():
    def __init__(self):
        event_system.subscribe(EventType.NOTIFY_CAREGIVER,self.notify_caregiver)
        event_system.subscribe(EventType.RESPONSE_CAREGIVER,self.get_caregivers)
        event_system.publish(EventType.REQUEST_CAREGIVER,'new')

    def get_caregivers(self, data):
        self.care_givers = data

    def notify_caregiver(self, text):
        for care_giver in self.care_givers:
            self.send_email("EMERGENCY", text, care_giver.email)

    def new_notification(self, message: str, type: NotificationType):  
        notification = Notification(
            notification_id=str(uuid.uuid4()),
            type = type.name,
            message=message,
            timestamp=datetime.now())
        
        event_system.publish(EventType.NOTIFICATION, notification)
    
    def send_email(self, subject, body, recipient): 
        '''
        Sends an email from the local SMTP server.
        Emails sent by this function are likely to go to the spam folder or get blocked by major email providers due to the absence of SPF, DKIM, and DMARC records.
        The domain 'mediremind.com' is configured on a local server for sending emails but lacks necessary DNS configurations
        '''
        sender = 'mail@mediremind.com'
        message = f"Subject: {subject}\n\n{body}"   
        with smtplib.SMTP('localhost') as server:
            server.sendmail(sender, recipient, message)

