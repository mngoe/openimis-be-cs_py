""" Model OpenIMIS Be Cheque Santé
Models of Cameroon Cheque Santé project
"""
import datetime
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import models
from core import models as core_models
from core.models import InteractiveUser
from django.http import request
from django.utils import timezone as django_tz 
import pandas as pd
import logging

logger = logging.getLogger(__name__)
class ChequeImport(models.Model):
    """ Class Cheque Import :
    Class for importation of check in the system
    """
    idChequeImport = models.AutoField(
        db_column="ChequeImportID",
        primary_key=True
    )
    importDate = models.DateTimeField(
        'Current Import Date', default=django_tz.now, blank=True
    )
    user = models.ForeignKey(
        core_models.InteractiveUser, models.DO_NOTHING, db_column="UserID"
    )
    stored_file = models.FileField(
        upload_to="csImports/%Y/%m/",
        db_column="ImportFile",
        default="",
        null=True,
        blank=True
    )

    """ Class Meta :
    Class Meta to define specific table
    """

    class Meta:
        db_table = "tblChequeSanteImport"

    @classmethod
    def update_specific_user_id(cls, id_cheque_exist):

        try:
            cls.objects.filter(idChequeImport=id_cheque_exist).update(user=request.user.id)
        except cls.DoesNotExist:
            print(f"Service  with id {id_cheque_exist} does not exist.")


def insert_data_to_cheque():
    if request.user.is_authenticated:
        ChequeImport.user = request.user.id
        ChequeImport.importDate = datetime.date.today()
        #views.upload_file()
        ChequeImport.save()
    else:
        raise NameError({
            'status': (
                'user is not authenticated'
            ),
        })


class ChequeImportLine(models.Model):
    """ Class Cheque Import Line :
    Class to save parsed CSV file uploaded and save all insert / update
    """
    idChequeImportLine = models.AutoField(primary_key=True)
    chequeImportId = models.ForeignKey(ChequeImport, models.DO_NOTHING)
    chequeImportLineCode = models.CharField(max_length=100)
    chequeImportLineDate = models.DateTimeField(
        'Current Import Date', default=django_tz.now, blank=True
    )
    chequeImportLineStatus = models.CharField(max_length=50)

    """ Class Meta :
    Class Meta to define specific table
    """

    class Meta:
        db_table = 'tblChequeSanteImportLine'


@dataclass
class UploadChequeResult:
    sent: int = 0
    created: int = 0
    updated: int = 0
    deleted: int = 0
    errors: int = 0


def upload_cheque_to_db(user, file):
    errors = []
    result = UploadChequeResult(errors=errors)

    try:
        user = InteractiveUser.objects.filter(login_name=user.username).first()
        chequeImportCreated = ChequeImport.objects.create(user=user, stored_file=file)
        ## Parsing CSV File to iterate on different lines
        tableChequeToImport = insert_data_to_cheque_line(
            chequeImportCreated.stored_file,
            chequeImportCreated
            )
        
        result.created += 1

    except Exception as exc:
        logger.exception(exc)
        print(exc);
        errors.append("An unknown error occured.")
    return result

def parse_csv_file(csv_file):
    data_parsed = pd.read_csv(csv_file)
    return data_parsed


def insert_data_to_cheque_line(csv_file, chequeImport):
    data_parsed = parse_csv_file(csv_file)
    for index, row in data_parsed.iterrows():
        statusValid = ['New', 'Used', 'Cancel']
        if row['ChequeStatus'] in statusValid :
            chequeImportLineInstance = ChequeImportLine()
            if ChequeImportLine.objects.filter(chequeImportLineCode=row['NumCheque']).exists():
                print("Code deja existant - Update ")
                print(ChequeImportLine.objects.filter(chequeImportLineCode=row['NumCheque']).get())
                
                chequeImportLineInstanceUpdate = ChequeImportLine.objects.filter(chequeImportLineCode=row['NumCheque']).first()
                chequeImportLineInstanceUpdate.chequeImportLineStatus = row['ChequeStatus']
                chequeImportLineInstanceUpdate.save()
                logger.exception("--------")
                logger.exception("Cheque Import Line Update :")
                logger.exception(row['NumCheque'])
                logger.exception(row['ChequeStatus'])
            else:
                chequeImportLineInstance.chequeImportId = chequeImport
                chequeImportLineInstance.chequeImportLineCode = row['NumCheque']
                chequeImportLineInstance.chequeImportLineStatus = row['ChequeStatus']
                chequeImportLineInstance.save()
                print("Code deja existant - Creation ")
                logger.exception("--------")
                logger.exception("Cheque Import Line Create :")
                logger.exception(row['NumCheque'])
                logger.exception(row['ChequeStatus'])
        else:
            print(" Import Cheque Statut anormal  ")
            logger.exception("--------")
            logger.exception("Import Cheque Statut anormal :")
            logger.exception(row['NumCheque'])
            logger.exception(row['ChequeStatus'])