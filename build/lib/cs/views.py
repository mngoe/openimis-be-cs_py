from io import TextIOWrapper
from django.http import HttpResponseRedirect
from django.shortcuts import render
from cs.models import ChequeImport, upload_cheque_to_db
from django.core import serializers
from cs import serialize
from rest_framework.decorators import api_view
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from django.http.response import JsonResponse
from django import utils
import logging
import pandas as pd

logger = logging.getLogger(__name__)

@api_view(["POST"])
def upload_cheque_file(request):
    serializer = serialize.UploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    errors = []
    file = serializer.validated_data.get("file")
    filename = serializer.validated_data.get("fileName")
    try:
        logger.info(f"Uploading cheque file in CSV format (file={file})...")
        logger.info(f"cheque upload completed: {request.user.id}")
        print(file)
        result = upload_cheque_to_db(
            request.user, file)
        logger.info(f"cheque upload completed: {result}")
    except Exception as exc:
        print(exc)
        logger.exception(exc)
        errors.append("An unknown error occurred.")
        errors.append(f"File '{file}' is not a valid CSV")

    return JsonResponse({"success": len(errors) == 0, "errors": errors})
