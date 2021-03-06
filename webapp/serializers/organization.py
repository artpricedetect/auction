from rest_framework import serializers
from webapp.models import organization


class OrganizationsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = organization.Organization
        fields = "__all__"  # 모든 필드 포함
        # fields = ["id", "name"] 처럼 직접 명시할 수도 있음


class OrganizationsCreateSerializer(serializers.Serializer):

    name = serializers.CharField(help_text="Organization Name", required=True)
    # CharField 외 FloatField, IntegerField, EmailField 등 여러 클래스 존재. 구글링 필요
