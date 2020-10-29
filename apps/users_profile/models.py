from django.db.models import (
    Model, OneToOneField, CharField, DateField, CASCADE, PositiveSmallIntegerField,
    ImageField, ManyToManyField, EmailField, DateTimeField, BooleanField, IntegerField,
)
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class Profile(Model):
    user = OneToOneField(
        "users_profile.User",
        on_delete=CASCADE,
        null=True
    )
    location = CharField(max_length=100)
    date_of_birth = DateField()
    sex_choices = (
        ('ML', 'Male'),
        ('FM', 'Female'),
        ('OT', 'other'),
    )
    sex = CharField(max_length=2, choices=sex_choices)
    status_choices = (
        (0, 'offline'),
        (1, 'online')
    )
    status = PositiveSmallIntegerField(default=0, choices=status_choices)
    main_quote = CharField(max_length=254, default="")
    nickname = CharField(max_length=20, unique=True)
    profession = CharField(max_length=50, default="")
    image = ImageField(upload_to='assets', max_length=None) 
    relationships = ManyToManyField('self',
        through='relationship.Relationship',
        symmetrical=False,
        related_name='related_to',
    )

class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = EmailField(max_length=254, unique=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    is_active = BooleanField(default=True)
    last_login = DateTimeField(null=True, blank=True)
    date_joined = DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)
    def get_email(self):
        return self.email

    class Meta:
        db_table = 'auth_user'



