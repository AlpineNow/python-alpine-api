from .alpineunittest import AlpineTestCase
from alpine import APIClient
from alpine.exception import *
from alpine.datasource import *
import time


class TestDataSource(AlpineTestCase):

    def setUp(self):
        super(TestDataSource, self).setUp()
        global db_datasource_id
        global hadoop_datasource_id
        global gpdb_datasource_name
        global hadoop_datasource_name
        # To pass the tests, we need a Hadoop Data Source with Name "API_Test_Hadoop"
        # and GPDB datas ource with name "API_Test_GPDB" created
        gpdb_datasource_name = "API_Test_GPDB"
        hadoop_datasource_name = "API_Test_Hadoop"
        database_name = "miner_demo"
        # Creating a Workspace for Job tests
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        db_datasource_id = alpine_session.datasource.get_id(gpdb_datasource_name, "Database")
        hadoop_datasource_id = alpine_session.datasource.get_id(hadoop_datasource_name, "Hadoop")

    def tearDown(self):
        # Drop the datasources created in setup
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)

    def test_get_db_data_source_list(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_list = alpine_session.datasource.get_list("Database")
        self.assertIsNotNone(datasource_list)

    def test_get_db_data_source_info(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_info = alpine_session.datasource.get(1, "Database")
        self.assertEqual(datasource_info['id'], 1)

    def test_get_db_data_source_id(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_id = alpine_session.datasource.get_id(gpdb_datasource_name, "Database")
        self.assertEqual(datasource_id, db_datasource_id)

    def test_get_hadoop_data_source_list(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_list = alpine_session.datasource.get_list("Hadoop")
        self.assertIsNotNone(datasource_list)

    def test_get_hadoop_data_source_info(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_info = alpine_session.datasource.get(hadoop_datasource_id, "Hadoop")
        self.assertEqual(datasource_info['name'], hadoop_datasource_name)

    def test_get_hadoop_data_source_id(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_id = alpine_session.datasource.get_id(hadoop_datasource_name, "Hadoop")
        self.assertEqual(datasource_id, hadoop_datasource_id)
