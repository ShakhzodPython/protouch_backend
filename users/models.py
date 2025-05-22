import uuid

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser

from utils.validation import validate_phone_number


# Create your models here.


class CustomerManager(BaseUserManager):
    """Custom manager for customer model without username"""

    def create_user(self, phone_number=None, email=None, password=None, **extra_fields):
        if phone_number is None and email is None:
            raise ValueError("User must have either phone number or email")

        extra_fields.setdefault("is_active", True)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)

        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, phone_number=None, email=None, password=None, **extra_fields
    ):
        """Create and return a superuser with phone number or email"""
        if phone_number is None and email is None:
            raise ValueError("User must have either phone number or email")

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            phone_number=phone_number, email=email, password=password, **extra_fields
        )


class Customer(AbstractUser):
    username = None
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, unique=True, editable=False
    )
    email = models.EmailField(verbose_name="Email", unique=True, null=True, blank=True)
    first_name = models.CharField(
        max_length=150, verbose_name="Fist name", null=True, blank=True
    )
    last_name = models.CharField(
        max_length=150, verbose_name="Last name", null=True, blank=True
    )
    phone_number = models.CharField(
        max_length=12,
        verbose_name="Phone number",
        unique=True,
        validators=[validate_phone_number],
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomerManager()

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.email if self.email else self.phone_number
