import pytest

from src.domain.value_objects.user import Email, RawPassword, Username, PhoneNumber, AvatarUrl
from src.domain.value_objects.order import OrderStatus
from src.domain.entities.order import Order
from src.domain.events.order import OrderCreated
from src.domain.errors.exceptions import InvalidEmailOrPasswordError, InvalidProfileDataError


def test_valid_email():
    email = Email("valid.user@example.com")
    assert email.value == "valid.user@example.com"


def test_invalid_email():
    with pytest.raises(InvalidEmailOrPasswordError):
        Email("invalid-email-address")


def test_valid_raw_password():
    pwd = RawPassword("StrongPassword123!")
    assert pwd.value == "StrongPassword123!"


def test_invalid_raw_passwords():
    # Too short
    with pytest.raises(InvalidEmailOrPasswordError, match="at least 8 characters"):
        RawPassword("Short1!")

    # Missing uppercase
    with pytest.raises(InvalidEmailOrPasswordError, match="uppercase"):
        RawPassword("lowercase123!")

    # Missing lowercase
    with pytest.raises(InvalidEmailOrPasswordError, match="lowercase"):
        RawPassword("UPPERCASE123!")

    # Missing digit
    with pytest.raises(InvalidEmailOrPasswordError, match="digit"):
        RawPassword("NoDigitsHere!")

    # Missing special character
    with pytest.raises(InvalidEmailOrPasswordError, match="special character"):
        RawPassword("NoSpecial123")


def test_username_validation():
    valid = Username("valid_user1")
    assert valid.value == "valid_user1"

    with pytest.raises(InvalidProfileDataError):
        Username("ab")  # Too short

    with pytest.raises(InvalidProfileDataError):
        Username("invalid user with spaces")


def test_phone_number_validation():
    valid = PhoneNumber("+84987654321")
    assert valid.value == "+84987654321"

    with pytest.raises(InvalidProfileDataError):
        PhoneNumber("invalid-phone")


def test_avatar_url_validation():
    valid_cloudinary = AvatarUrl("https://res.cloudinary.com/test/image.png")
    assert valid_cloudinary.value == "https://res.cloudinary.com/test/image.png"

    valid_generic = AvatarUrl("https://example.com/avatar.webp?size=small")
    assert valid_generic.value == "https://example.com/avatar.webp?size=small"

    # Non-image files or invalid schemes should fail at domain level
    with pytest.raises(InvalidProfileDataError):
        AvatarUrl("https://random-site.com/document.pdf")

    with pytest.raises(InvalidProfileDataError):
        AvatarUrl("ftp://example.com/image.png")

    with pytest.raises(InvalidProfileDataError):
        AvatarUrl("invalid-url-string")


def test_order_creation_and_event():
    order = Order.create(
        id="order-123",
        user_id="user-456",
        user_email="buyer@example.com",
        amount=100000,
        status=OrderStatus.PENDING
    )

    assert order.id == "order-123"
    assert order.amount == 100000
    assert order.status == OrderStatus.PENDING
    assert len(order.events) == 1
    event = order.events[0]
    assert isinstance(event, OrderCreated)
    assert event.order_id == "order-123"
    assert event.amount == 100000
