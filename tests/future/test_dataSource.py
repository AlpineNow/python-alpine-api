from alpineunittest import AlpineTestCase
from alpine.apiclient import APIClient
from future.datasource import *

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

    def test_add_greenplum_data_source(self):
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
        alpine_session = APIClient(self.host, self.port)
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

    def test_delete_db_data_source(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        ds.delete_db_data_source_if_exists("Test_GP_delete")
        ds.add_greenplum_data_source("Test_GP_delete", "Test Greenplum", "10.10.0.151", 5432,
                                                                  "miner_demo", "miner_demo", "miner_demo")
        response = ds.delete_db_data_source("Test_GP_delete")
        self.assertEqual(response.status_code, 200)
        try:
            alpine_session.datasource.get("Test_GP_delete","Database")
        except DataSourceNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Datasource {0}".format("Test_GP_delete"))

    def test_delete_hadoop_data_source(self):
        alpine_session = APIClient(self.host, self.port)
        alpine_session.login(self.username, self.password)
        ds.delete_hadoop_data_source_if_exists("Test_Cloudera_delete")
        additional_parameters = [
            {"key": "mapreduce.jobhistory.address", "value": "awscdh57singlenode.alpinenow.local:10020"},
            {"key": "mapreduce.jobhistory.webapp.address", "value": "awscdh57singlenode.alpinenow.local:19888"},
            {"key": "yarn.app.mapreduce.am.staging-dir", "value": "/tmp"},
            {"key": "yarn.resourcemanager.admin.address", "value": "awscdh57singlenode.alpinenow.local:8033"},
            {"key": "yarn.resourcemanager.resource-tracker.address",
             "value": "awscdh57singlenode.alpinenow.local:8031"},
            {"key": "yarn.resourcemanager.scheduler.address", "value": "awscdh57singlenode.alpinenow.local:8030"}
        ]
        ds.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera_delete", "Test Cloudera",
                                                  "awscdh57singlenode.alpinenow.local", 8020,
                                                  "awscdh57singlenode.alpinenow.local", 8032,
                                                  "yarn", "hadoop", additional_parameters
                                                  )
        response = ds.delete_hadoop_data_source("Test_Cloudera_delete")
        self.assertEqual(response.status_code, 200)
        try:
            alpine_session.datasource.get("Test_Cloudera_delete", "Hadoop")
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
