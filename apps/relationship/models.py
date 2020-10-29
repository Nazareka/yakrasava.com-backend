from django.db import models

from apps.users_profile.models import Profile

class Relationship(models.Model):
    from_profile = models.ForeignKey(Profile,
        related_name='from_user',
        on_delete=models.CASCADE,
    )
    to_profile = models.ForeignKey(Profile,
        related_name='to_user',
        on_delete=models.CASCADE,
    )
    status = models.CharField(max_length=20)