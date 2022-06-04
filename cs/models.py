import uuid
from django.db import models
from core import models as core_models

class ChequeImport(models.Model):
    id = models.AutoField(db_column="ChequeImportID", primary_key=True)
    importDate = models.DateField()
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

    class Meta:
        db_table = "tblChequeSanteImport"
