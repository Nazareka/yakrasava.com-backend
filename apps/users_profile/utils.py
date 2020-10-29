from __future__ import annotations

from django.db.models import Q
from django.db.models.manager import BaseManager
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework.renderers import JSONRenderer

from typing import Dict, Tuple, Sequence, NewType, Union, Tuple, List
from typing_extensions import Literal
from mypy_extensions import TypedDict

from apps.relationship.models import Relationship

from . import models
from . import types
from . import serializers

def get_list_related_users(
    list_relationships_related_users: BaseManager[Relationship], 
    related: str
) -> BaseManager[models.Profile]:
    
    if related == "from":
        list_ids_related_users = list_relationships_related_users.values_list('to_profile_id')
    else:
        list_ids_related_users = list_relationships_related_users.values_list('from_profile_id')

    list_related_users_and_status = models.Profile.objects.filter(
        id__in=list_ids_related_users
    )

    return list_related_users_and_status

def get_full_profile_with_rs_status_another_user(
    current_profile_id: int, 
    another_profile_id: int, 
    another_profile_object: models.Profile
) -> Dict:
    
    try:
        rs_from_current_profile_to_another = Relationship.objects.get(
            from_profile=current_profile_id, 
            to_profile=another_profile_id
        )
        profile_dict = serializers.FullProfileSerializer(another_profile_object)
        data = {
            'profile': profile_dict.data, 
            'related': 'from',
            'status': rs_from_current_profile_to_another.status
        } 
        return data
    except Relationship.DoesNotExist:
        try:
            rs_from_another_user_to_current = Relationship.objects.get(
                from_profile=another_profile_id, 
                to_profile=current_profile_id
            )
            profile_dict = serializers.FullProfileSerializer(another_profile_object)
            data = {
                'profile': profile_dict.data, 
                'related': 'to',
                'status': rs_from_another_user_to_current.status
            }
            return data
        except Relationship.DoesNotExist:
            profile_dict = serializers.FullProfileSerializer(another_profile_object)
            data = {
                'profile': profile_dict.data, 
                'related': 'none',
                'status': 'none'
            }
            return data