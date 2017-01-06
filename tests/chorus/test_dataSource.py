from chorusunittest import ChorusTestCase
from api.chorus.chorus import Chorus
from api.chorus.datasource import DataSource
from api.exception import *


class TestDataSource(ChorusTestCase):

    def setUp(self):
        super(TestDataSource, self).setUp()
        global db_datasource_id
        global hadoop_datasource_id
        # Creating a Database Datasource for test get/update functions
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_session.delete_db_data_source_if_exists("Test_GP")
        datasource = datasource_session.add_greenplum_data_source("Test_GP", "Test Greenplum", "10.10.0.151", 5432,
                                                                  "miner_demo", "miner_demo", "miner_demo")
        db_datasource_id = datasource['id']
        # Creating a Hadoop Datasource for test get/update functions
        datasource_session.delete_hadoop_data_source_if_exists("Test_Cloudera")
        additional_parameters = [
            {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
            {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
            {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
            {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
            {"key": "yarn.resourcemanager.resource-tracker.address",
             "value": "awscdh57singlenode.alpinenow.local:8031"},
            {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
        ]
        datasource_hadoop = datasource_session.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera", "Test Cloudera",
                                              "awscdh57singlenode.alpinenow.local", 8020,
                                              "awscdh57singlenode.alpinenow.local", 8032,
                                              "yarn", "hadoop", additional_parameters
                                              )

        hadoop_datasource_id = datasource_hadoop['id']

    def tearDown(self):
        # Drop the datasources created in setup
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_session.delete_db_data_source_if_exists("Test_GP")
        datasource_session.delete_db_data_source_if_exists("Test_Cloudera")

    def test_add_greenplum_data_source(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_session.delete_db_data_source_if_exists("Test_GP_add")
        datasource = datasource_session.add_greenplum_data_source("Test_GP_add", "Test Greenplum", "10.10.0.151", 5432,
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
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_session.delete_hadoop_data_source_if_exists("Test_Cloudera_add")
        additional_parameters = [
            {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
            {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
            {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
            {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
            {"key": "yarn.resourcemanager.resource-tracker.address", "value": "awscdh57singlenode.alpinenow.local:8031"},
            {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
        ]
        datasource = datasource_session.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera_add","Test Cloudera",
                                                               "awscdh57singlenode.alpinenow.local", 8020,
                                                               "awscdh57singlenode.alpinenow.local", 8032,
                                                               "yarn", "hadoop",additional_parameters
                                                               )
        self.assertEqual(datasource['name'], "Test_Cloudera_add")

    def test_add_hadoop_hive_data_source(self):
        self.fail()

    def test_get_db_data_source_list(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_list = datasource_session.get_db_data_source_list()
        self.assertIsNotNone(datasource_list)

    def test_get_db_data_source_info(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_info = datasource_session.get_db_data_source_info("Test_GP")
        self.assertEqual(datasource_info['name'], "Test_GP")

    def test_get_db_data_source_id(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_id = datasource_session.get_db_data_source_id("Test_GP")
        self.assertEqual(datasource_id, db_datasource_id)

    def test_delete_db_data_source(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_session.delete_db_data_source_if_exists("Test_GP_delete")
        datasource_session.add_greenplum_data_source("Test_GP_delete", "Test Greenplum", "10.10.0.151", 5432,
                                                                  "miner_demo", "miner_demo", "miner_demo")
        response = datasource_session.delete_db_data_source("Test_GP_delete")
        self.assertEqual(response.status_code, 200)
        try:
            datasource_session.get_db_data_source_info("Test_GP_delete")
        except DataSourceNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Datasource {0}".format("Test_GP_delete"))

    def test_get_hadoop_data_source_list(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_list = datasource_session.get_hadoop_data_source_list()
        self.assertIsNotNone(datasource_list)

    def test_get_hadoop_data_source_info(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_info = datasource_session.get_hadoop_data_source_info("Test Cloudera")
        self.assertEqual(datasource_info['name'], "Test Cloudera")

    def test_get_hadoop_data_source_id(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_id = datasource_session.get_hadoop_data_source_id("Test Cloudera")
        self.assertEqual(datasource_id, hadoop_datasource_id)

    def test_delete_hadoop_data_source(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_session.delete_hadoop_data_source_if_exists("Test_Cloudera_delete")
        additional_parameters = [
            {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
            {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
            {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
            {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
            {"key": "yarn.resourcemanager.resource-tracker.address",
             "value": "awscdh57singlenode.alpinenow.local:8031"},
            {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
        ]
        datasource_session.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera_delete", "Test Cloudera",
                                                  "awscdh57singlenode.alpinenow.local", 8020,
                                                  "awscdh57singlenode.alpinenow.local", 8032,
                                                  "yarn", "hadoop", additional_parameters
                                                  )
        response = datasource_session.delete_hadoop_data_source("Test_Cloudera_delete")
        self.assertEqual(response.status_code, 200)
        try:
            datasource_session.get_db_data_source_info("Test_Cloudera_delete")
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
