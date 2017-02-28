from alpineunittest import AlpineTestCase
from api.alpine import Alpine
from api.exception import *
from future.datasource import *
import time

class TestDataSource(AlpineTestCase):

    def setUp(self):
        super(TestDataSource, self).setUp()
        global db_datasource_id
        global hadoop_datasource_id
        # Creating a Database Datasource for test get/update functions
        alpine_session = Alpine(self.host, self.port)
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
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        ds = DataSource(alpine_session.base_url, alpine_session.session, alpine_session.token)

        ds.delete_db_data_source_if_exists("Test_GP")
        ds.delete_db_data_source_if_exists("Test_Cloudera")

    def test_add_greenplum_data_source(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        ds = DataSource(alpine_session.base_url, alpine_session.session, alpine_session.token)

        ds.delete_db_data_source_if_exists("Test_GP_add")
        datasource = ds.add_greenplum_data_source("Test_GP_add", "Test Greenplum", "10.10.0.151", 5432,
                                                                  "miner_demo","miner_demo", "miner_demo")
        self.assertEqual(datasource['name'], "Test_GP_add")

    def test_add_postgres_data_source(self):
        self.fail()

    def test_add_hawq_data_source(self):
        self.fail()

    def test_add_oracle_data_source(self):
        self.fail()

    def test_add_jdbc_data_source(self):
        self.fail()

    def test_add_jdbc_hive_data_source(self):
        self.fail()

    def test_add_hadoop_data_source(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        ds = DataSource(alpine_session.base_url, alpine_session.session, alpine_session.token)

        ds.delete_hadoop_data_source_if_exists("Test_Cloudera_add")
        additional_parameters = [
            {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
            {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
            {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
            {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
            {"key": "yarn.resourcemanager.resource-tracker.address", "value": "awscdh57singlenode.alpinenow.local:8031"},
            {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
        ]
        datasource = ds.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera_add","Test Cloudera",
                                                               "awscdh57singlenode.alpinenow.local", 8020,
                                                               "awscdh57singlenode.alpinenow.local", 8032,
                                                               "yarn", "hadoop",additional_parameters
                                                               )
        self.assertEqual(datasource['name'], "Test_Cloudera_add")

    def test_add_hadoop_hive_data_source(self):
        self.fail()

    def test_get_db_data_source_list(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_list = alpine_session.datasource.get_list("Database")
        self.assertIsNotNone(datasource_list)

    def test_get_db_data_source_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_info = alpine_session.datasource.get("Database", 1)
        self.assertEqual(datasource_info['id'], 1)

    def test_get_db_data_source_id(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_id = alpine_session.datasource.get_db_data_source_id("Test_GP")
        self.assertEqual(datasource_id, db_datasource_id)

    def test_delete_db_data_source(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.datasource.delete_db_data_source_if_exists("Test_GP_delete")
        alpine_session.datasource.add_greenplum_data_source("Test_GP_delete", "Test Greenplum", "10.10.0.151", 5432,
                                                                  "miner_demo", "miner_demo", "miner_demo")
        response = alpine_session.datasource.delete_db_data_source("Test_GP_delete")
        self.assertEqual(response.status_code, 200)
        try:
            alpine_session.datasource.get_db_data_source_info("Test_GP_delete")
        except DataSourceNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Datasource {0}".format("Test_GP_delete"))

    def test_get_hadoop_data_source_list(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_list = alpine_session.datasource.get_list("Hadoop")
        self.assertIsNotNone(datasource_list)

    def test_get_hadoop_data_source_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_info = alpine_session.datasource.get_hadoop_data_source_info("Test_Cloudera")
        self.assertEqual(datasource_info['name'], "Test_Cloudera")

    def test_get_hadoop_data_source_id(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_id = alpine_session.datasource.get_hadoop_data_source_id("Test_Cloudera")
        self.assertEqual(datasource_id, hadoop_datasource_id)

    def test_delete_hadoop_data_source(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.datasource.delete_hadoop_data_source_if_exists("Test_Cloudera_delete")
        additional_parameters = [
            {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
            {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
            {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
            {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
            {"key": "yarn.resourcemanager.resource-tracker.address",
             "value": "awscdh57singlenode.alpinenow.local:8031"},
            {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
        ]
        alpine_session.datasource.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera_delete", "Test Cloudera",
                                                  "awscdh57singlenode.alpinenow.local", 8020,
                                                  "awscdh57singlenode.alpinenow.local", 8032,
                                                  "yarn", "hadoop", additional_parameters
                                                  )
        response = alpine_session.datasource.delete_hadoop_data_source("Test_Cloudera_delete")
        self.assertEqual(response.status_code, 200)
        try:
            alpine_session.datasource.get_db_data_source_info("Test_Cloudera_delete")
        except DataSourceNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Datasource {0}".format("Test_Cloudera_delete"))

    def test_get_db_data_source_username(self):
        self.fail()

    def test_enable_db_data_source(self):
        self.fail()

    def test_disable_db_data_source(self):
        self.fail()

    def test_enable_hdfs_data_source(self):
        self.fail()

    def test_disable_hdfs_data_source(self):
        self.fail()

    def test_add_user_to_datasource(self):
        self.fail()

    def test_get_users_on_a_data_source(self):
        self.fail()

    def test_remove_user_from_datasource(self):
        self.fail()

    def test_change_owner_of_datasource(self):
        self.fail()
