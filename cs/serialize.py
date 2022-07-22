from rest_framework_xml.renderers import XMLRenderer

from rest_framework import serializers


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


def format_diagnosis(diagnosis):
    return {"diagnosis_code": diagnosis.code, "diagnosis_name": diagnosis.name}
