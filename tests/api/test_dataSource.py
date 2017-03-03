from .alpineunittest import AlpineTestCase
from alpine import APIClient
from alpine.exception import *
from alpine.datasource import *
from future.datasource import *
import time

class TestDataSource(AlpineTestCase):

    def setUp(self):
        super(TestDataSource, self).setUp()
        global db_datasource_id
        global hadoop_datasource_id
        global ds
        # Creating a Database Datasource for test get/update functions
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        ds = DataSource(alpine_session.base_url, alpine_session.session, alpine_session.token)

        ds.delete_db_data_source_if_exists("Test_GP")
        datasource = ds.add_greenplum_data_source("Test_GP", "Test Greenplum", "10.10.0.151", 5432,
                                                                  "miner_demo", "miner_demo", "miner_demo")
        db_datasource_id = datasource['id']
        # Creating a Hadoop Datasource for test get/update functions
        ds.delete_hadoop_data_source_if_exists("Test_Cloudera")
        additional_parameters = [
            {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
            {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
            {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
            {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
            {"key": "yarn.resourcemanager.resource-tracker.address",
             "value": "awscdh57singlenode.alpinenow.local:8031"},
            {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
        ]
        datasource_hadoop = ds.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera", "Test Cloudera",
                                              "awscdh57singlenode.alpinenow.local", 8020,
                                              "awscdh57singlenode.alpinenow.local", 8032,
                                              "yarn", "hadoop", additional_parameters
                                              )

        hadoop_datasource_id = datasource_hadoop['id']
        hadoop_datasource_id = alpine_session.datasource.get_id("Test_Cloudera")

    def tearDown(self):
        # Drop the datasources created in setup
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        ds = DataSource(alpine_session.base_url, alpine_session.session, alpine_session.token)

        ds.delete_db_data_source_if_exists("Test_GP")
        ds.delete_db_data_source_if_exists("Test_Cloudera")

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
        datasource_id = alpine_session.datasource.get_id("Test_GP", "Database")
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
        self.assertEqual(datasource_info['name'], "Test_Cloudera")

    def test_get_hadoop_data_source_id(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_id = alpine_session.datasource.get_id("Test_Cloudera", "Hadoop")
        self.assertEqual(datasource_id, hadoop_datasource_id)
