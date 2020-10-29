from django.contrib import admin
from django.urls import path, include
from django.urls import include, path

from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users_profile.views import ProfileViewSet
from apps.relationship.views import ChangeRelationshipView
from apps.chating.views import ChatViewSet, ChatMessageViewSet

router = SimpleRouter()
router.register(r'api', ProfileViewSet, basename='ProfileViewSet')
router.register(r'api', ChatViewSet, basename='ChatViewSet')
router.register(r'api', ChatMessageViewSet, basename='ChatMessageViewSet')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/change_relationship/', ChangeRelationshipView.as_view()),
    path('', include(router.urls)),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
