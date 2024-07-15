import graphene
from core import ExtendedConnection, prefix_filterset
from core.schema import OpenIMISMutation, OrderedDjangoFilterConnectionField, DjangoObjectType
from cs.models import ChequeImportLine, ChequeImport
import graphene
from cs.models import ChequeImportLine, ChequeUpdatedHistory
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from core.utils import TimeUtils
import graphene_django_optimizer as gql_optimizer
from django.db.models import Q
from core.models import InteractiveUser

class ChequeImportLineGQLType(DjangoObjectType):
    class Meta:
        model = ChequeImportLine
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "chequeImportLineCode": ["exact", "icontains"],
            "chequeImportLineStatus": ["exact","icontains"],
            "chequeImportLineDate": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


class ChequeImportGQLType(DjangoObjectType):
    class Meta:
        model = ChequeImport
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "user": ["exact"],
            "importDate": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection

class ChequeUpdatedHistoryGQLType(DjangoObjectType):
    class Meta:
        model = ChequeUpdatedHistory
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "user": ["exact"],
            # "importDate": ["exact", "lt", "lte", "gt", "gte"],
        }
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    chequeimportline = OrderedDjangoFilterConnectionField(
        ChequeImportLineGQLType,
        diagnosisVariance=graphene.Int(),
        code_is_not=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
        items=graphene.List(of_type=graphene.String),
        services=graphene.List(of_type=graphene.String),
    )

    chequeimport = OrderedDjangoFilterConnectionField(
        ChequeImportGQLType,
        diagnosisVariance=graphene.Int(),
        code_is_not=graphene.String(),
        orderBy=graphene.List(of_type=graphene.String),
        items=graphene.List(of_type=graphene.String),
        services=graphene.List(of_type=graphene.String),
    )

    ChequeUpdatedHistories = OrderedDjangoFilterConnectionField(ChequeUpdatedHistoryGQLType)
    def resolve_ChequeUpdatedHistories(self, info, **kwargs):
        filters = []
        ids = kwargs.get('id', None)
        if ids:
            filters.append(Q(id=ids))
        return gql_optimizer.query(ChequeUpdatedHistory.objects.filter(*filters).all(), info)


class ChequeUpdatedHistoryInputType(OpenIMISMutation.Input):
    idChequeUpdated = graphene.Int(required=False)
    chequeImportLine = graphene.Int(required=True)
    user = graphene.Int(required=True)
    updated_date = graphene.DateTime(required=False)
    description = graphene.String(required=True)

class ChequeImportLineInputType(OpenIMISMutation.Input):
    idChequeImportLine = graphene.Int(required=True)
    chequeImportId = graphene.Int(required=False)
    chequeImportLineCode = graphene.String(required=False)
    chequeImportLineDate = graphene.DateTime(required=False)
    chequeImportLineStatus = graphene.String(required=True)

statusValid = ['New', 'Used', 'Cancel']

# methode de mise a jour du statut de cheque
def update_cheque_status(data, user):
    if "client_mutation_id" in data:
        data.pop('client_mutation_id')
    if "client_mutation_label" in data:
        data.pop('client_mutation_label')
    idChequeImportLine = data.pop('idChequeImportLine') if 'idChequeImportLine' in data else None
    if idChequeImportLine:
        cheque = ChequeImportLine.objects.get(idChequeImportLine=idChequeImportLine)
        old_status = cheque.chequeImportLineStatus 

        new_status = data.get('chequeImportLineStatus')
        if new_status not in statusValid:
            raise Exception(f"Invalid cheque status: {new_status}. Must be one of {statusValid}")

        [setattr(cheque, key, data[key]) for key in data]
        cheque.save()

        # Creation de l'hitorique
        create_cheque_updated_history(user, idChequeImportLine, old_status, data['chequeImportLineStatus'])

    else:
        raise Exception("Cheque %s does not exist")%(idChequeImportLine)
    return cheque

# methode de creation de l'hitorique
def create_cheque_updated_history(user, idChequeImportLine, old_status, new_status):
    try:
        chequeImportLine = ChequeImportLine.objects.get(idChequeImportLine=idChequeImportLine)

        user_instance = InteractiveUser.objects.get(id=user.id_for_audit)
        updated_date = TimeUtils.now()
        description = f"The status has been changed from {old_status} to {new_status}."
        ChequeUpdatedHistory.objects.create(
            user=user_instance,
            updated_date=updated_date,
            description=description,
            chequeImportLine=chequeImportLine
        )
    except Exception as exc:
        return [{
            'message': ("cs.mutation.failed_to_create_chequeUpdatedHistory"),
            'detail': str(exc)
        }]


class UpdateChequeStatusMutation(OpenIMISMutation):

    """
    This mutation will update a ChequeStatus
    """

    _mutation_module = "cs"
    _mutation_class = "UpdateChequeStatusMutation"
    
    class Input(ChequeImportLineInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):

        try:
            if type(user) is AnonymousUser or not user.id:
                raise ValidationError(
                    ("mutation.authentication_required"))
            data['audit_user_id'] = user.id_for_audit
            update_cheque_status(data, user)
            
            return  None 
        except Exception as exc:
            return [{
                'message': ("cs.mutation.failed_to_update_chequeStatus"),
                'detail': str(exc)}]
        



class Mutation(graphene.ObjectType):
    update_cheque_status = UpdateChequeStatusMutation.Field()

