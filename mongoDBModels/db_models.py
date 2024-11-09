from mongoengine import (Document, StringField, IntField, DateField, ListField,\
                         NotUniqueError,EmbeddedDocument, EmbeddedDocumentField,\
EmailField,ReferenceField,DateTimeField)
from datetime import datetime, timezone
import bcrypt
import re



class User(Document):
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)  # Note: In a real application, hash the password
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))

    meta = {'collection': 'users'}
    
    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
		
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
	
    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        return super(User, self).save(*args, **kwargs)
	
    def validate_email(self):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, self.email):
            raise ValueError("Invalid email format")


class Milestone(EmbeddedDocument):
    id = StringField()
    title = StringField(required=True)
    description = StringField()
    target_date = DateTimeField()
    status = StringField(default="Pending")
    completed_date = DateTimeField()

class Reminder(EmbeddedDocument):
    id = StringField()
    reminder_date = DateTimeField(required=True)
    message = StringField(required=True)

class Note(EmbeddedDocument):
    id = StringField()
    note_date = DateTimeField(required=True)
    content = StringField(required=True)

class Goal(Document):
    user_id = StringField(required=True)
    title = StringField(required=True)
    description = StringField()
    category = StringField()
    start_date = DateTimeField()
    end_date = DateTimeField()
    status = StringField(default="In Progress")
    progress = IntField(default=0)
    milestones = ListField(EmbeddedDocumentField(Milestone))
    reminders = ListField(EmbeddedDocumentField(Reminder))
    notes = ListField(EmbeddedDocumentField(Note))
    tags = ListField(StringField())
    created_at = DateTimeField()
    updated_at = DateTimeField()

    meta = {'collection': 'goals'}
	


