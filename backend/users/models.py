from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for both students and teachers.
    """

    # Roles
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (STUDENT, "Student"),
        (TEACHER, "Teacher"),
        (ADMIN, "Admin"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=STUDENT
    )

    # Profile details
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # More specific than country
    date_of_birth = models.DateField(blank=True, null=True)

    # Optional demographic info
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    # Verification & activity
    is_verified = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
