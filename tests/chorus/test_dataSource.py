from chorusunittest import ChorusTestCase
from api.chorus.chorus import Chorus
from api.chorus.datasource import DataSource
from api.exception import *


class TestDataSource(ChorusTestCase):

    def test_add_greenplum_data_source(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_session.delete_db_data_source_if_exists("Test_GP")
        datasource = datasource_session.add_greenplum_data_source("Test_GP", "Test Greenplum", "10.10.0.151", 5432,
                                                                  "miner_demo","miner_demo", "miner_demo")
        self.assertEqual(datasource['name'], "Test_GP")

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
        datasource_session.delete_hadoop_data_source_if_exists("Test_Cloudera")
        datasource = datasource_session.add_hadoop_data_source("Cloudera CDH5.4-5.7", "Test_Cloudera","Test Cloudera",
                                                               "awscdh57singlenode.alpinenow.local", 8020,
                                                               "awscdh57singlenode.alpinenow.local", 8032,
                                                               "yarn", "hadoop", ""
                                                               )
        self.assertEqual(datasource['name'], "Test_Cloudera")

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
        datasource_info = datasource_session.get_db_data_source_info("test")
        self.assertEqual(datasource_info['name'], "test")

    def test_get_db_data_source_id(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_id = datasource_session.get_db_data_source_id("test")
        self.assertEqual(datasource_id, 2)
        #TODO Validation

    def test_delete_db_data_source(self):
        chorus_session = Chorus(self.host, self.port)
        chorus_session.login(self.username, self.password)
        datasource_session = DataSource(chorus_session)
        datasource_session.delete_db_data_source_if_exists("Test_GP")
        datasource_session.add_greenplum_data_source("Test_GP", "Test Greenplum", "10.10.0.151", 5432,
                                                                  "miner_demo", "miner_demo", "miner_demo")
        response = datasource_session.delete_db_data_source("Test_GP")
        self.assertEqual(response.status_code, 200)
        try:
            datasource_session.get_db_data_source_info("Test_GP")
        except DataSourceNotFoundException:
            pass
        else:
            self.fail("Failed to Delete the Datasource {0}".format("Test_GP"))

    def test_get_database_id(self):
        self.fail()

    def test__get_hdfs_data_source_id(self):
        self.fail()

    def test__get_db_data_source_id(self):
        self.fail()

    def test_get_hdfs_data_source_list(self):
        self.fail()



    def test_get_hdfs_data_source_details(self):
        self.fail()

    def test_get_hdfs_root_dir_list(self):
        self.fail()

    def test_get_hdfs_sub_dir_list(self):
        self.fail()

    def test_get_db_data_source_details(self):
        self.fail()

    def test_get_db_database_list(self):
        self.fail()

    def test_get_data_source_schema_list(self):
        self.fail()

    def test_get_db_schema_list(self):
        self.fail()

    def test_get_db_dataset_list(self):
        self.fail()

    def test_get_db_data_source_username(self):
        self.fail()

    def test_delete_hdfs_data_source(self):
        self.fail()



    def test_change_data_source_state(self):
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

    def test_get_user_id_on_datasource(self):
        self.fail()

    def test_remove_user_from_datasource(self):
        self.fail()

    def test_change_owner_of_datasource(self):
        self.fail()
