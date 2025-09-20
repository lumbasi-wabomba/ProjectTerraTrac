from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterUserView,
    LoginView,
    LogoutUserView,
    TerratracUserViewSet,
    ForestAreaViewSet,
    NDVIRecordViewSet,
    AlertViewSet,
    CommunityReportViewSet,
    NDVICalcView
)

router = DefaultRouter()
router.register(r'users', TerratracUserViewSet, basename='user')
router.register(r'forest-areas', ForestAreaViewSet, basename='forest-area')
router.register(r'ndvi-records', NDVIRecordViewSet, basename='ndvi-record')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'community-reports', CommunityReportViewSet, basename='community-report')

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('ndvi_calc/', NDVICalcView.as_view(), name='ndvi')
]
urlpatterns += router.urls