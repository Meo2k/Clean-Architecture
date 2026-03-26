from datetime import datetime, timedelta
import pytest

from src.domain.entities.user import User
from src.domain.value_objects.user import Email, HashedPassword, Username, PhoneNumber, AvatarUrl
from src.domain.events.user import PasswordChangedEvent
from src.domain.errors.exceptions import UserLockedError


def test_create_user():
    username = Username("john_doe")
    email = Email("john@example.com")
    hashed_pwd = HashedPassword("hashed_secret_123")

    user = User.create(username=username, email=email, hashed_password=hashed_pwd)

    assert user.id is not None
    assert isinstance(user.id, str)
    assert user.username == username
    assert user.email == email
    assert user.password == hashed_pwd
    assert user.status is True
    assert user.failed_login_attempts == 0
    assert user.locked_until is None


def test_change_password_dispatches_event():
    user = User.create(
        username=Username("john_doe"),
        email=Email("john@example.com"),
        hashed_password=HashedPassword("old_hash")
    )
    new_hash = HashedPassword("new_hash_456")

    user.change_password(new_hash)

    assert user.password == new_hash
    assert len(user.events) == 1
    event = user.events[0]
    assert isinstance(event, PasswordChangedEvent)
    assert event.user_id == user.id
    assert event.user_email == "john@example.com"


def test_verify_password_success_resets_counter():
    user = User.create(
        username=Username("john_doe"),
        email=Email("john@example.com"),
        hashed_password=HashedPassword("correct_hash")
    )
    user.failed_login_attempts = 3

    verify_fn = lambda raw, hashed: raw == "secret" and hashed == "correct_hash"
    is_valid = user.verify_password("secret", verify_fn=verify_fn)

    assert is_valid is True
    assert user.failed_login_attempts == 0
    assert user.locked_until is None


def test_verify_password_failure_increments_attempts_and_locks():
    user = User.create(
        username=Username("john_doe"),
        email=Email("john@example.com"),
        hashed_password=HashedPassword("correct_hash")
    )

    verify_fn = lambda raw, hashed: False

    # 4 failed attempts (max is 5)
    for _ in range(4):
        valid = user.verify_password("wrong", verify_fn=verify_fn, max_attempts=5)
        assert valid is False

    assert user.failed_login_attempts == 4
    assert user.locked_until is None

    # 5th attempt locks the account
    valid = user.verify_password("wrong", verify_fn=verify_fn, max_attempts=5, lock_duration=timedelta(minutes=15))
    assert valid is False
    assert user.failed_login_attempts == 5
    assert user.locked_until is not None
    assert user.locked_until > datetime.now()

    # Next attempt should raise UserLockedError
    with pytest.raises(UserLockedError):
        user.verify_password("any_password", verify_fn=verify_fn)


def test_update_profile():
    user = User.create(
        username=Username("initial_user"),
        email=Email("user@example.com"),
        hashed_password=HashedPassword("hashed")
    )

    new_username = Username("updated_user")
    new_phone = PhoneNumber("+1234567890")
    new_avatar = AvatarUrl("https://res.cloudinary.com/demo/image/upload/sample.jpg")

    user.update_profile(
        username=new_username,
        phone_number=new_phone,
        avatar_url=new_avatar,
        bio="Hello world"
    )

    assert user.username == new_username
    assert user.phone_number == new_phone
    assert user.avatar_url == new_avatar
    assert user.bio == "Hello world"
