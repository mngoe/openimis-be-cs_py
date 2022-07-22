from io import TextIOWrapper
from django.http import HttpResponseRedirect
from django.shortcuts import render
from cs.models import ChequeImport, upload_cheque_to_db
from django.core import serializers
# from cs.models import ChequeImport
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

# Create your views here.


logger = logging.getLogger(__name__)


""""@require_http_methods(["POST"])
def upload_cheques(request):
    if not request.user.has_perms():
        raise PermissionDenied(_("unauthorized"))

    if not request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    errors = []
    for file in request.FILES:
        try:
            logger.info(f"Processing cheque in {file}")
            csv_file = request.FILES[file]
            upload_cheque_to_db(request.user, csv_file)
        except Exception as exc:
            logger.exception(exc)
            errors.append("An unknown error occured.")
            errors.append(f"File '{file}' is not a valid CSV")
            continue

    return JsonResponse({"success": len(errors) == 0, "errors": errors})
"""


""""@require_http_methods(["POST"])
def upload_cheques(request):
    if not request.user.has_perms():
        raise PermissionDenied(_("unauthorized"))

    if not request.FILES:
        return JsonResponse({"error": "No file provided"}, status=400)

    errors = []
    for file in request.FILES:
        try:
            logger.info(f"Processing cheque in {file}")
            csv_file = request.FILES[file]
            upload_cheque_to_db(request.user, csv_file)
        except Exception as exc:
            logger.exception(exc)
            errors.append("An unknown error occured.")
            errors.append(f"File '{file}' is not a valid CSV")
            continue

    return JsonResponse({"success": len(errors) == 0, "errors": errors})
"""


@api_view(["POST"])
def upload_cheque_file(request):
    serializer = serialize.UploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    errors = []
    file = serializer.validated_data.get("file")
    try:
        logger.info(f"Uploading cheque file in CSV format (file={file})...")
        result = upload_cheque_to_db(
            request.user.id, store_file=file)
        logger.info(f"cheque upload completed: {result}")
    except Exception as exc:
        logger.exception(exc)
        errors.append("An unknown error occurred.")
        errors.append(f"File '{file}' is not a valid CSV")

    return JsonResponse({"success": len(errors) == 0, "errors": errors})
