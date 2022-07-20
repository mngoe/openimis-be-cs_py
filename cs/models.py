""" Model OpenIMIS Be Cheque Santé
Models of Cameroon Cheque Santé project
"""
import datetime

from django.core.exceptions import ValidationError
from django.db import models
from core import models as core_models
from django.http import request
import pandas as pd


from cs import views


class ChequeImport(models.Model):
    """ Class Cheque Import :
    Class for importation of check in the system
    """
    idChequeImport = models.AutoField(
        db_column="ChequeImportID",
        primary_key=True
    )
    importDate = models.DateTimeField()
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
        views.upload_file[1]
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
    chequeImportLineDate = models.DateTimeField()
    chequeImportLineStatus = models.CharField(max_length=50)

    """ Class Meta :
    Class Meta to define specific table
    """

    class Meta:
        db_table = 'tblChequeSanteImportLine'



def parse_csv_file(csv_file):  # json_file is the returned file uploaded by upload_file function
    data_parsed = pd.read_csv(csv_file)
    return data_parsed


def insert_data_to_cheque_line(self):
    data_parsed = parse_csv_file(views.upload_file[1])
    for i in range(len(data_parsed)):
        if ChequeImportLine.objects.filter(chequeImportLineCode=data_parsed.values[i][0]).exists():
            id_import_value = ChequeImportLine.objects.filter(chequeImportLineCode=data_parsed.values[i][0])
            [0][ChequeImportLine.chequeImportId]
            ChequeImport.update_specific_user_id(id_import_value)
            ChequeImportLine.chequeImportLineCode = data_parsed.values[i][0]
            ChequeImportLine.chequeImportId = id_import_value
            ChequeImportLine.chequeImportLineDate = datetime.date.today()
            ChequeImportLine.chequeImportLineStatus = data_parsed.values[i][1]
            ChequeImportLine.save()
        else:
            if ChequeImport.objects.filter(user=request.user.id).exists():

                ChequeImportLine.chequeImportId = ChequeImport.objects.filter(user=request.user.id)
                [0][ChequeImport.idChequeImport]
                ChequeImportLine.chequeImportLineCode = data_parsed.values[i][0]
                ChequeImportLine.chequeImportLineDate = datetime.date.today()
                ChequeImportLine.chequeImportLineStatus = data_parsed.values[i][1]
                ChequeImportLine.save()
            else:
                print(f"User  with id {ChequeImport.idChequeImport} does not exist.")
