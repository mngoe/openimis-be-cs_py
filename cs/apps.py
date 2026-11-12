from django.apps import AppConfig

MODULE_NAME = "cs"

# Cheques (cheque santé) are a national register with no location of their own:
# they are protected by rights, not by districts. cs has no right of its own, so
# the defaults mirror the frontend (fe-cmr-cs CmrCsModuleMainMenu), which shows the
# cheque screens to a user holding ANY of the claim rights 111002..111007.
# Each list is read as "any of"; override through ModuleConfiguration("cs").
CLAIM_RIGHTS = ["111002", "111003", "111004", "111005", "111006", "111007"]

DEFAULT_CFG = {
    "gql_query_cheques_perms": CLAIM_RIGHTS,
    "gql_mutation_update_cheques_perms": CLAIM_RIGHTS,
    "cheque_upload_perms": CLAIM_RIGHTS,
}


class CsConfig(AppConfig):
    name = MODULE_NAME

    gql_query_cheques_perms = []
    gql_mutation_update_cheques_perms = []
    cheque_upload_perms = []

    def __load_config(self, cfg):
        for field in cfg:
            if hasattr(CsConfig, field):
                setattr(CsConfig, field, cfg[field])

    def ready(self):
        from core.models import ModuleConfiguration

        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self.__load_config(cfg)


def has_any_right(user, perms):
    """True when `user` is authenticated and holds at least one right of `perms`.

    An empty list refuses: a missing configuration must not mean open.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    return any(user.has_perms([perm]) for perm in (perms or []))
