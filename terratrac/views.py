from django.shortcuts import render
from .serializers import TerratracUserSerializer, ForestAreaSerializer, NDVIRecordSerializer, AlertSerializer, CommunityReportSerializer, VerificationSerializer
from .models import TerratracUser, ForestArea, NDVIRecord, Alert, CommunityReport, Verification
from .ndvi import calc_ndvi
from django.contrib.auth import authenticate, get_user_model
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from datetime import datetime

# Create your views here.
class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TerratracUserSerializer(data=request.data)
        if serializer.is_valid():
            User = get_user_model()
            user = User.objects.create_user(**serializer.validated_data)
            #token, _ = Token.objects.get_or_create(user=user)
            return Response({
               # 'token': token.key,
                'user': TerratracUserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username_or_email = request.data.get("username") 
        password = request.data.get("password")
        user = authenticate(username=username_or_email, password=password)

        if not user:
            try:
                User = get_user_model()
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        if not user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        request.session['auth_token'] = token.key
        return Response({"token": token.key}, status=status.HTTP_200_OK)

class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()
        request.session.pop('token', None)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

    
class TerratracUserViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TerratracUserSerializer
    queryset = TerratracUser.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return TerratracUser.objects.all()
        return TerratracUser.objects.filter(id=user.id)

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


    def perform_destroy(self, instance):
        if self.request.user != instance and not self.request.user.is_staff:
            raise PermissionDenied("You cannot delete another user’s account.")
        instance.delete()
    
class ForestAreaViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ForestAreaSerializer
    queryset = ForestArea.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['name', 'latitude', 'longitude', 'last_ndvi']

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can create forest areas.")
        serializer.save()

    def partial_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can update forest areas.")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_staff:
            raise PermissionDenied("Only staff can delete forest areas.")
        instance.delete()

    
class AlertViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = AlertSerializer
    queryset = Alert.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['forest_area__name', 'alert_type', 'status', 'triggered_on']

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def verify(self, request, pk=None):
        alert = self.get_object()
        if alert.status != 'Pending':
            return Response({'error': 'Alert has already been verified or rejected.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid():
            verification = serializer.save(alert=alert, verified_by=request.user)
            perform_verify(verification)
            return Response(VerificationSerializer(verification).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NDVIRecordViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = NDVIRecordSerializer
    queryset = NDVIRecord.objects.all()

class CommunityReportViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommunityReportSerializer
    queryset = CommunityReport.objects.all()
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['reported_by__username', 'latitude', 'longitude', 'submitted_on']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CommunityReport.objects.all()
        return CommunityReport.objects.filter(reported_by=user)

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to raise a report.")
        report = serializer.save(reported_by=self.request.user)

        alert = Alert.objects.create(
            forest_area=report.forest_area,
            alert_type="Deforestation",
            change_value=-0.00000000000000001,
            status="Pending",
            triggered_on=datetime.now().date()
        )
        report.linked_alerts.add(alert)

    def partial_update(self, serializer):
        report = self.get_object()
        if self.request.user != report.reported_by and not self.request.user.is_staff:
            raise PermissionDenied("You cannot update someone else's report.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.reported_by and not self.request.user.is_staff:
            raise PermissionDenied("You cannot delete someone else's report.")
        instance.delete()

class NDVICalcView(APIView):
    def post(self, request):
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        forest_area_name = request.data.get("forest_name") 

        calculations = calc_ndvi(latitude, longitude)
        ndvi_value = calculations.mean_ndvi(start_date, end_date)

        response_data = {"ndvi": ndvi_value}

        if forest_area_name:
            try:
                forest_area = ForestArea.objects.get(name=forest_area_name)
            except ForestArea.DoesNotExist:
                return Response({"error": "Forest area not found."}, status=404)

            record = NDVIRecord.objects.create(
                forest_area=forest_area,
                ndvi_values=ndvi_value
            )
            serializer = NDVIRecordSerializer(record)
            response_data.update(serializer.data)

        return Response(response_data, status=201)
