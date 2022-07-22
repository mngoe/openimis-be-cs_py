import graphene
from core import ExtendedConnection, prefix_filterset
from core.schema import OrderedDjangoFilterConnectionField, DjangoObjectType
from cs.models import ChequeImportLine, ChequeImport


class ChequeImportLineGQLType(DjangoObjectType):
    class Meta:
        model = ChequeImportLine
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "chequeImportLineCode": ["exact"],
            "chequeImportLineStatus": ["exact", "icontains"],
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
