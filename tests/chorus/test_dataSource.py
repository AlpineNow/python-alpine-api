from api.alpine import Alpine
from api.datasource import DataSource
from api.exception import *
from chorusunittest import ChorusTestCase


class TestDataSource(ChorusTestCase):

    def setUp(self):
        super(TestDataSource, self).setUp()
        global db_datasource_id
        global hadoop_datasource_id
        # Creating a Database Datasource for test get/update functions
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.datasource.delete_db_data_source_if_exists("Test_GP")
        datasource = alpine_session.datasource.add_greenplum_data_source("Test_GP", "Test Greenplum", "10.10.0.151", 5432,
                                                                  "miner_demo", "miner_demo", "miner_demo")
        db_datasource_id = datasource['id']
        # Creating a Hadoop Datasource for test get/update functions
        alpine_session.datasource.delete_hadoop_data_source_if_exists("Test_Cloudera")
        additional_parameters = [
            {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
            {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
            {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
            {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
            {"key": "yarn.resourcemanager.resource-tracker.address",
             "value": "awscdh57singlenode.alpinenow.local:8031"},
            {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
        ]
        datasource_hadoop = alpine_session.datasource.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera", "Test Cloudera",
                                              "awscdh57singlenode.alpinenow.local", 8020,
                                              "awscdh57singlenode.alpinenow.local", 8032,
                                              "yarn", "hadoop", additional_parameters
                                              )

        hadoop_datasource_id = datasource_hadoop['id']

    def tearDown(self):
        # Drop the datasources created in setup
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.datasource.delete_db_data_source_if_exists("Test_GP")
        alpine_session.datasource.delete_db_data_source_if_exists("Test_Cloudera")

    def test_add_greenplum_data_source(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        alpine_session.datasource.delete_db_data_source_if_exists("Test_GP_add")
        datasource = alpine_session.datasource.add_greenplum_data_source("Test_GP_add", "Test Greenplum", "10.10.0.151", 5432,
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
        alpine_session.datasource.delete_hadoop_data_source_if_exists("Test_Cloudera_add")
        additional_parameters = [
            {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
            {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
            {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
            {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
            {"key": "yarn.resourcemanager.resource-tracker.address", "value": "awscdh57singlenode.alpinenow.local:8031"},
            {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
        ]
        datasource = alpine_session.datasource.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera_add","Test Cloudera",
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
        datasource_list = alpine_session.datasource.get_db_data_source_list()
        self.assertIsNotNone(datasource_list)

    def test_get_db_data_source_info(self):
        alpine_session = Alpine(self.host, self.port)
        alpine_session.login(self.username, self.password)
        datasource_info = alpine_session.datasource.get_db_data_source_info("Test_GP")
        self.assertEqual(datasource_info['name'], "Test_GP")

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
        datasource_list = alpine_session.datasource.get_hadoop_data_source_list()
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
