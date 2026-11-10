"""
Security tests for cs (cheque santé): API rights.

Cheques are a national register with no location, so they are protected by rights
only. cs declares no right of its own; the defaults mirror the frontend menu
(fe-cmr-cs), which opens the cheque screens to a holder of ANY claim right
111002..111007. Tags: [NEW] no reference equivalent (cs is Cameroon specific).

Run: manage.py test cs.test_security_parity --keepdb
"""
import json

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from core.models.openimis_graphql_test_case import openIMISGraphQLTestCase
from core.test_helpers import create_right_only_user, get_test_token
from cs.models import ChequeImport, ChequeImportLine

SUBMIT_CLAIM = 111007  # one of the claim rights opening the cheque screens
SEARCH_CLAIM = 111001  # a claim right outside that range

CHEQUES_GQL = '{ chequeimportline(chequeImportLineCode: "SPCS001") { edges { node { chequeImportLineCode } } } }'
HISTORY_GQL = '{ ChequeUpdatedHistories { edges { node { description } } } }'


class _Base:
    @classmethod
    def make_users(cls):
        cls.cheque_user = create_right_only_user("spcs_cheque", [SUBMIT_CLAIM])
        cls.other_right = create_right_only_user("spcs_other", [SEARCH_CLAIM])
        cls.no_right = create_right_only_user("spcs_noright", [])
        cheque_import = ChequeImport.objects.create(user=cls.cheque_user.i_user)
        cls.cheque = ChequeImportLine.objects.create(
            chequeImportId=cheque_import, chequeImportLineCode="SPCS001",
            chequeImportLineStatus="New")


class ChequeQueryRightsTest(_Base, openIMISGraphQLTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.make_users()

    def setUp(self):
        cache.clear()

    def _query(self, query, user=None):
        headers = {"HTTP_AUTHORIZATION": f"Bearer {get_test_token(user)}"} if user else {}
        return json.loads(self.query(query, headers=headers).content)

    def test_anonymous_cannot_list_cheques(self):
        content = self._query(CHEQUES_GQL)
        self.assertIn("errors", content)
        self.assertFalse((content.get("data") or {}).get("chequeimportline"))

    def test_user_without_a_cheque_right_cannot_list_cheques(self):
        for user in (self.no_right, self.other_right):
            content = self._query(CHEQUES_GQL, user)
            self.assertIn("errors", content, user.username)
            self.assertFalse((content.get("data") or {}).get("chequeimportline"), user.username)

    def test_user_without_a_cheque_right_cannot_read_the_history(self):
        content = self._query(HISTORY_GQL, self.no_right)
        self.assertIn("errors", content)

    def test_control_cheque_right_lists_cheques(self):
        content = self._query(CHEQUES_GQL, self.cheque_user)
        self.assertNotIn("errors", content, content)
        codes = [e["node"]["chequeImportLineCode"] for e in content["data"]["chequeimportline"]["edges"]]
        self.assertEqual(["SPCS001"], codes)


class ChequeMutationRightsTest(_Base, TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.make_users()

    def setUp(self):
        cache.clear()

    def _update(self, user, status):
        from cs.schema import UpdateChequeStatusMutation
        errors = UpdateChequeStatusMutation.async_mutate(
            user, idChequeImportLine=self.cheque.idChequeImportLine,
            chequeImportLineStatus=status)
        return errors, ChequeImportLine.objects.get(pk=self.cheque.pk).chequeImportLineStatus

    def test_user_without_a_cheque_right_cannot_change_a_status(self):
        errors, status = self._update(self.no_right, "Cancel")
        self.assertTrue(errors)
        self.assertEqual("New", status, "cheque status changed without a cheque right")

    def test_control_cheque_right_changes_a_status(self):
        errors, status = self._update(self.cheque_user, "Cancel")
        self.assertFalse(errors, errors)
        self.assertEqual("Cancel", status)


class ChequeUploadRightsTest(_Base, TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.make_users()

    def setUp(self):
        cache.clear()

    def _upload(self, user=None):
        client = APIClient()
        if user is not None:
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {get_test_token(user)}")
        csv = SimpleUploadedFile("cheques.csv", b"NumCheque,ChequeStatus\nSPCS002,New\n",
                                 content_type="text/csv")
        return client.post(f"/{settings.SITE_ROOT()}cs/importfile/upload",
                           {"file": csv}, format="multipart")

    def test_anonymous_cannot_upload_cheques(self):
        response = self._upload(None)
        self.assertIn(response.status_code, (401, 403))
        self.assertFalse(ChequeImportLine.objects.filter(chequeImportLineCode="SPCS002").exists())

    def test_user_without_a_cheque_right_cannot_upload_cheques(self):
        response = self._upload(self.no_right)
        self.assertEqual(403, response.status_code)
        self.assertFalse(ChequeImportLine.objects.filter(chequeImportLineCode="SPCS002").exists())
