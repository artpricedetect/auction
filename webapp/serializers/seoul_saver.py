from rest_framework import serializers


class SeoulSaverSerializer(serializers.Serializer):

    sale_no = serializers.CharField(help_text="Sale No", required=True)
