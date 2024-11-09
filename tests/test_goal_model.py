import pytest
from datetime import datetime, timedelta
from mongoengine import connect, disconnect
import mongomock
from db_models import Goal, Milestone, Reminder, Note  # Assuming your models are in a file named models.py


@pytest.fixture(scope="module")
def mongo_test_setup():
    # Connect using mongomock.MongoClient
    connect("GOAL_TRACKER", host="localhost", mongo_client_class=mongomock.MongoClient)
    yield
    # Disconnect after tests
    disconnect()


def test_goal_creation(mongo_test_setup):
    # Create embedded documents
    milestone = Milestone(
        title="Complete the first draft",
        description="Finish the initial draft of the project",
        target_date=datetime.now() + timedelta(days=30)
    )

    reminder = Reminder(
        reminder_date=datetime.now() + timedelta(days=5),
        message="Check progress and update milestones"
    )

    note = Note(
        note_date=datetime.now(),
        content="This project is crucial for Q4 goals"
    )

    # Create a Goal document
    goal = Goal(
        user_id="user123",
        title="Launch New Product",
        description="Goal to prepare and launch the new product",
        category="Product Development",
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=90),
        progress=10,
        milestones=[milestone],
        reminders=[reminder],
        notes=[note],
        tags=["product", "Q4", "launch"],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Save and verify document creation
    goal.save()
    retrieved_goal = Goal.objects(user_id="user123").first()

    assert retrieved_goal is not None
    assert retrieved_goal.title == "Launch New Product"
    assert retrieved_goal.category == "Product Development"
    assert len(retrieved_goal.milestones) == 1
    assert retrieved_goal.milestones[0].title == "Complete the first draft"
    assert len(retrieved_goal.reminders) == 1
    assert retrieved_goal.reminders[0].message == "Check progress and update milestones"
    assert len(retrieved_goal.notes) == 1
    assert retrieved_goal.notes[0].content == "This project is crucial for Q4 goals"


def test_goal_update(mongo_test_setup):
    # Retrieve and update the goal document
    goal = Goal.objects(user_id="user123").first()
    goal.progress = 50
    goal.status = "In Progress"
    goal.updated_at = datetime.now()
    goal.save()

    # Retrieve and check if update was successful
    updated_goal = Goal.objects(user_id="user123").first()

    assert updated_goal.progress == 50
    assert updated_goal.status == "In Progress"


def test_goal_deletion(mongo_test_setup):
    # Delete the goal document
    goal = Goal.objects(user_id="user123").first()
    goal.delete()

    # Check if the document was deleted
    deleted_goal = Goal.objects(user_id="user123").first()
    assert deleted_goal is None
