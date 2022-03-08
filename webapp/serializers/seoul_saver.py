from rest_framework import serializers


class SeoulCreateSerializer(serializers.Serializer):

    sale_no = serializers.CharField(help_text="Sale No", required=True)
