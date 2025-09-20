from rest_framework import serializers
from .models import Badge, TerratracUser, ForestArea, NDVIRecord, Alert, CommunityReport, Verification
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator

class TerratracUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    badges = serializers.SlugRelatedField(queryset=Badge.objects.all(), slug_field='name', many=True, required=False)
    phone_num = serializers.CharField(validators=[RegexValidator(r'^\+?1?\d{9,15}$')])
    class Meta:
        model = TerratracUser
        fields = '__all__'
        read_only_fields = ['points', 'badges']

class ForestAreaSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = serializers.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    last_ndvi = serializers.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)], required=False)
    last_date_checked = serializers.DateField(required=False)
    class Meta:
        model = ForestArea
        fields = '__all__'
        read_only_fields = ['last_ndvi', 'last_date_checked']

class NDVIRecordSerializer(serializers.ModelSerializer):
    forest_area = serializers.SlugRelatedField(queryset=ForestArea.objects.all(), slug_field='name')
    class Meta:
        model = NDVIRecord
        fields = '__all__'
        read_only_fields = ['image_taken_date','ndvi_values']

class AlertSerializer(serializers.ModelSerializer):
    forest_area = serializers.SlugRelatedField(queryset=ForestArea.objects.all(), slug_field='name')

    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['triggered_on']

class CommunityReportSerializer(serializers.ModelSerializer):
    reported_by = serializers.SlugRelatedField(queryset=TerratracUser.objects.all(), slug_field='username')
    #alerts = serializers.PrimaryKeyRelatedField(queryset=Alert.objects.all(), many=True, write_only=True)
    forest_area = serializers.SlugRelatedField(queryset=ForestArea.objects.all(),  slug_field='name')
    linked_alerts = AlertSerializer( read_only=True, many=True)
    latitude = serializers.FloatField(validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = serializers.FloatField(validators=[MinValueValidator(-180), MaxValueValidator(180)])
    class Meta:
        model = CommunityReport
        fields = '__all__'
        read_only_fields = ['submitted_on', 'image']
        

class VerificationSerializer(serializers.ModelSerializer):
    verified_by = serializers.SlugRelatedField(queryset=TerratracUser.objects.all(), slug_field='username')
    alert = serializers.SlugRelatedField(queryset=Alert.objects.all(), slug_field='alert_type')

    class Meta:
        model = Verification
        fields = '__all__'
        read_only_fields = ['timestamp']

def perform_verify(instance):
    if instance.status == 'Pending':
        instance.verified = True
        instance.save()
    return f"Verification status is already updated"

