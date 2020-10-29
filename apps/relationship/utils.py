from __future__ import annotations

from django.db.models import Q
from django.db.models.manager import BaseManager
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist

from apps.users_profile.models import Profile
from . import models


def get_list_relationships_friends_by_profile_id(
    profile_id: int
) -> BaseManager[models.Relationship]:

    list_relationships_friends = models.Relationship.objects.filter(
        Q(from_profile=profile_id, status="friend") |
        Q(from_profile=profile_id, status="close_friend") |
        Q(from_profile=profile_id, status="relative") |
        Q(from_profile=profile_id, status="beloved")
    )

    return list_relationships_friends

def get_list_relationships_followers_by_profile_id(
    profile_id: int
) -> BaseManager[models.Relationship]:

    list_relationships_followers = models.Relationship.objects.filter(
        to_profile=profile_id, 
        status="follow"
    )

    return list_relationships_followers

def get_list_relationships_follows_by_profile_id(
    profile_id: int
) -> BaseManager[models.Relationship]:

    list_relationships_follows = models.Relationship.objects.filter(
        from_profile=profile_id, 
        status="follow"
    )
    
    return list_relationships_follows

def follow_user(
    current_profile_id: int, 
    another_profile_id: int
) -> None:
    current_user = Profile.objects.get(id=current_profile_id)
    friend_user = Profile.objects.get(id=another_profile_id)

    current_user.relationships.add(friend_user)
    current_user_relationship = models.Relationship.objects.get(from_profile=current_profile_id, to_profile=another_profile_id)
    current_user_relationship.status = 'follow'
    current_user_relationship.save()

def unfollow_user(
    current_profile_id: int, 
    another_profile_id: int
) -> None:
    current_user = Profile.objects.get(id=current_profile_id)
    another_user = Profile.objects.get(id=another_profile_id)

    current_user.relationships.remove(another_user)

def make_user_friend(
    current_profile_id: int, 
    another_profile_id: int
) -> None:
    current_user = Profile.objects.get(id=current_profile_id)
    another_user = Profile.objects.get(id=another_profile_id)

    current_user.relationships.add(another_user)
    current_user_relationship = models.Relationship.objects.get(
        from_profile=current_profile_id, 
        to_profile=another_profile_id
    )
    another_user_relationship = models.Relationship.objects.get(
        to_profile=current_profile_id, 
        from_profile=another_profile_id
    )
    another_user_relationship.status = 'friend'
    current_user_relationship.status = 'friend'
    another_user_relationship.save()
    current_user_relationship.save()

def unfriend_user(
    current_profile_id: int, 
    another_profile_id: int
    ) -> None:
    current_user_relationship = models.Relationship.objects.get(
        from_profile=current_profile_id, 
        to_profile=another_profile_id
    )
    another_user_relationship = models.Relationship.objects.get(
        to_profile=current_profile_id, 
        from_profile=another_profile_id
    )
    another_user_relationship.status = 'follow'
    another_user_relationship.save()
    current_user_relationship.delete()

def make_special_friend(
    current_profile_id: int, 
    another_profile_id: int,
    status: str
) -> None:

    current_user_relationship = models.Relationship.objects.get(
        from_profile=current_profile_id, to_profile=another_profile_id
    )
    current_user_relationship.status = status
    current_user_relationship.save()

def make_user_close_friend(
    current_profile_id: int, 
    another_profile_id: int
) -> None:
    make_special_friend(current_profile_id, another_profile_id, 'close_friend')

def make_user_relative(
    current_profile_id: int, 
    another_profile_id: int
) -> None:
    make_special_friend(current_profile_id, another_profile_id, 'relative')

def make_user_beloved(
    current_profile_id: int, 
    another_profile_id: int
) -> None:
    make_special_friend(current_profile_id, another_profile_id, 'beloved')

def unmake_user_special_friend(
    current_profile_id: int, 
    another_profile_id: int
) -> None:

    current_user_relationship = models.Relationship.objects.get(
        from_profile=current_profile_id, 
        to_profile=another_profile_id
    )
    current_user_relationship.status = 'friend'
    current_user_relationship.save()


