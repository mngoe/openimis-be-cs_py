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
    updatedCheques = []

globalUpdatedCheques = []

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

        # Ajout des chèques mis à jour à la liste et Réinitialisation de la liste !!!
        result.updatedCheques.extend(globalUpdatedCheques)
        globalUpdatedCheques.clear()

    except Exception as exc:
        logger.exception(exc)
        print(exc);
        errors.append("An unknown error occured.")
    return result

def parse_csv_file(csv_file):
    data_parsed = pd.read_csv(csv_file, converters={i: str for i in range(100)})
    return data_parsed


def insert_data_to_cheque_line(csv_file, chequeImport):
    data_parsed = parse_csv_file(csv_file)
    
    for index, row in data_parsed.iterrows():
        statusValid = ['New', 'Used', 'Cancel'] 
        lengthValid = [6,7,8]

        normalized_status = row['ChequeStatus'].capitalize()
        # if row['ChequeStatus'] in statusValid and len(row['NumCheque']) == 6 :
        if normalized_status in statusValid and len(row['NumCheque']) in lengthValid :
            chequeImportLineInstance = ChequeImportLine()
            if ChequeImportLine.objects.filter(chequeImportLineCode=row['NumCheque']).exists():
                print("Code deja existant - Update ")
                chequeImportGet = ChequeImportLine.objects.filter(chequeImportLineCode=row['NumCheque']).first()
                if chequeImportGet.chequeImportLineStatus != "Used":
                    chequeImportLineInstanceUpdate = ChequeImportLine.objects.filter(chequeImportLineCode=row['NumCheque']).first()
                    chequeImportLineInstanceUpdate.chequeImportLineStatus = normalized_status
                    chequeImportLineInstanceUpdate.save()
                    globalUpdatedCheques.append((chequeImportLineInstanceUpdate.idChequeImportLine, row['NumCheque'], normalized_status, chequeImportLineInstanceUpdate.chequeImportLineDate))
                    logger.info("Cheque Import Line Update : %s", row['NumCheque'])
                    logger.info("normalized status %s", normalized_status)
                else:
                    globalUpdatedCheques.append((chequeImportGet.idChequeImportLine, row['NumCheque'], "Used", chequeImportGet.chequeImportLineDate))
            else:
                chequeImportLineInstance.chequeImportId = chequeImport
                chequeImportLineInstance.chequeImportLineCode = row['NumCheque']
                chequeImportLineInstance.chequeImportLineStatus = normalized_status
                chequeImportLineInstance.save()
                logger.info("Cheque Import Line Create : %s", row['NumCheque'])
                logger.info("normalized status %s", normalized_status)
        else:
            if normalized_status in statusValid:
                logger.info("Import Cheque Statut anormal : %s", row['NumCheque'])
                logger.info("normalized status %s", normalized_status)
            # if len(row['NumCheque']) != 6:
            if len(row['NumCheque']) not in lengthValid:
                logger.info("Import Cheque Code anormal : %s", row['NumCheque'])
                logger.info("normalized status %s", normalized_status)

    if globalUpdatedCheques:
        logger.info("Chèques existants mis à jour:")
        for idChequeImportLine, cheque_code, new_status, chequeImportLineDate in globalUpdatedCheques:
            logger.info(
                "Id: %s, Code: %s, Nouveau statut: %s, Date d'importation: %s",
                idChequeImportLine, cheque_code, new_status, chequeImportLineDate
            )


class ChequeUpdatedHistory(models.Model):
    idChequeUpdated = models.AutoField(
        db_column="ChequeUpdatedID",
        primary_key=True
    )
    chequeImportLine = models.ForeignKey(ChequeImportLine, models.DO_NOTHING)
    user = models.ForeignKey(
        core_models.InteractiveUser, models.DO_NOTHING, db_column="UserID"
    )
    updated_date = models.DateTimeField(
        'Current Updated Date', default=django_tz.now, blank=True
    )
    description = models.TextField(max_length=200)
    
    class Meta:
        db_table = "cheque_updated_history"
