import json
from api.exception import *
from api.alpineobject import AlpineObject


class DataSource(AlpineObject):

    def __init__(self, base_url=None, session=None, token = None):
        super(DataSource, self).__init__(base_url, session, token)

    ###--- DB Data Source Functions ---###
    def get_db_data_source_list(self, per_page=100):
        """

        :param per_page:
        :return:
        """
        datasource_list = None
        url = "{0}/data_sources".format(self.base_url)
        url = self._add_token_to_url(url)
        self.logger.debug("Getting list of Database data sources from {0}".format(url))
        page_current = 0
        while True:
            payload = {
                "all": True,
                "per_page": per_page,
                "page": page_current + 1,
            }
            datasource_list_response = self.session.get(url, params=payload, verify=False).json()
            page_total = datasource_list_response['pagination']['total']
            page_current = datasource_list_response['pagination']['page']
            if datasource_list:
                datasource_list.extend(datasource_list_response['response'])
            else:
                datasource_list = datasource_list_response['response']
            if page_total == page_current:
                break
        return datasource_list

    def get_db_data_source_info(self, name):
        """

        :param name:
        :return:
        """
        ds_list = self.get_db_data_source_list()
        for db_ds in ds_list:
            if db_ds['name'] == name:
                return db_ds
        raise DataSourceNotFoundException("Datasource {0} is not found.".format(name))

    def get_db_data_source_id(self, name):
        """

        :param name:
        :return:
        """
        ds = self.get_db_data_source_info(name)
        return ds['id']

    def add_greenplum_data_source(self, name, description, host_name, port, db_name, db_username, db_password,
                           share_type=False, public=True, ssl=False, state="online"):
        """

        :param name:
        :param description:
        :param host_name:
        :param port:
        :param db_name:
        :param db_username:
        :param db_password:
        :param share_type:
        :param public:
        :param ssl:
        :param state:
        :return:
        """
        db_type = "gpdb_data_source"
        return self._add_db_data_source(db_type, name, description, host_name, port, db_name, db_username, db_password,
                                 share_type, public, ssl, state)

    def add_postgres_data_source(self, name, description, host_name, port, db_name, db_username, db_password,
                           share_type=False, public=True, ssl=False, state="online"):
        """

        :param name:
        :param description:
        :param host_name:
        :param port:
        :param db_name:
        :param db_username:
        :param db_password:
        :param share_type:
        :param public:
        :param ssl:
        :param state:
        :return:
        """
        db_type = "pg_data_source"
        return self._add_db_data_source(db_type, name, description, host_name, port, db_name, db_username, db_password,
                                 share_type, public, ssl, state)

    def _add_db_data_source(self, db_type, name, description, host_name, port, db_name, db_username, db_password,
                           share_type=False, public=True, ssl=False, state="online",
                           disable_kerberos_impersonation=False, high_availability=False):
        """
        Test
        :param db_type:
        :param name:
        :param description:
        :param host_name:
        :param port:
        :param db_name:
        :param db_username:
        :param db_password:
        :param share_type:
        :param public:
        :param ssl:
        :param state:
        :param disable_kerberos_impersonation:
        :param high_availability:
        :return:
        """
        url = "{0}/data_sources".format(self.base_url)
        url = self._add_token_to_url(url)
        payload = {"name": name,
                   "entity_type": db_type,
                   "description": description,
                   "host": host_name,
                   "port": port,
                   "db_name": db_name,
                   "db_username": db_username,
                   "db_password": db_password,
                   "shared": str(share_type),
                   "public": str(public),
                   "state": str(state),
                   "ssl": str(ssl),
                   "disable_kerberos_impersonation": disable_kerberos_impersonation,
                   "high_availability": high_availability
                   }
        self.logger.debug("POSTING payload:...{0}...to {1}".format(payload, url))

        response = self.session.post(url, data=payload, verify=False)
        self.logger.debug("Received response ode {0} with reason {1}...".format(response.status_code, response.reason))
        return response.json()['response']

    def delete_db_data_source(self, name):
        """

        :param name:
        :return:
        """
        data_source_id = self.get_db_data_source_id(name)
        url = "{0}/data_sources/{1}".format(self.base_url, data_source_id)
        url = self._add_token_to_url(url)
        self.logger.debug("DELETing data source {0}".format(name))
        response = self.session.delete(url)
        self.logger.debug("Received response code {0} with reason {1}".format(response.status_code, response.reason))
        return response

    def delete_db_data_source_if_exists(self, name):
        """

        :param name:
        :return:
        """
        try:
            self.delete_db_data_source(name)
        except DataSourceNotFoundException:
            self.logger.debug("Data source {0} not found, we don't need to delete it".format(name))

    ###--- Hadoop Data Sources ---###
    def get_hadoop_data_source_list(self, per_page=100):
        """

        :param per_page:
        :return:
        """
        datasource_list = None
        url = "{0}/hdfs_data_sources".format(self.base_url)
        url = self._add_token_to_url(url)
        self.logger.debug("Getting list of HDFS data sources from {0}".format(url))
        page_current = 0
        while True:
            payload = {
                "per_page": per_page,
                "page": page_current + 1,
            }
            datasource_list_response = self.session.get(url, data=json.dumps(payload), verify=False).json()
            page_total = datasource_list_response['pagination']['total']
            page_current = datasource_list_response['pagination']['page']
            if datasource_list:
                datasource_list.extend(datasource_list_response['response'])
            else:
                datasource_list = datasource_list_response['response']
            if page_total == page_current:
                break
        return datasource_list

    def get_hadoop_data_source_info(self, name):
        """

        :param name:
        :return:
        """
        ds_list = self.get_hadoop_data_source_list()
        for db_ds in ds_list:
            if db_ds['name'] == name:
                return db_ds
        raise DataSourceNotFoundException("HDFS Datasource {0} is not found.".format(name))

    def get_hadoop_data_source_id(self, name):
        """

        :param name:
        :return:
        """
        ds = self.get_hadoop_data_source_info(name)
        return ds['id']

    def add_hadoop_data_source(self, hadoop_version, name, description, name_node_host, namenode_port,
                                   resource_manager_host, resource_manager_port, username, group_list,
                                   connection_parameters,
                                   share_type=False, public=True, state="online", high_availability=False,
                                   use_kerberos=False, disable_kerberos_impersonation=False, ssl=False):
        """

        :param hadoop_version:
        :param name:
        :param description:
        :param name_node_host:
        :param namenode_port:
        :param resource_manager_host:
        :param resource_manager_port:
        :param username:
        :param group_list:
        :param connection_parameters:
        :param share_type:
        :param public:
        :param state:
        :param high_availability:
        :param use_kerberos:
        :param disable_kerberos_impersonation:
        :param ssl:
        :return:
        """
        self.session.headers.update({"Content-Type": "application/json"})  # Set special header for this post

        url = "{0}/hdfs_data_sources".format(self.base_url)
        url = self._add_token_to_url(url)
        payload = {"name": name,
                   "hdfs_version": hadoop_version,
                   "description": description,
                   "host": name_node_host,
                   "port": str(namenode_port),
                   "job_tracker_host": resource_manager_host,
                   "job_tracker_port": str(resource_manager_port),
                   "username": username,
                   "group_list": group_list,
                   "high_availability": high_availability,
                   "shared": share_type,
                   "connection_parameters": connection_parameters,
                   "state": state,
                   "public": public,
                   "uses_kerberos": use_kerberos,
                   "disable_kerberos_impersonation": disable_kerberos_impersonation,
                   "third_party_security_enabled": False, #TODO
                   "ssl": ssl
                   }
        self.logger.debug("POSTING payload:...{0}...to {1}".format(payload, url))
        payload = json.dumps(payload)
        response = self.session.post(url, data=payload, verify=False)
        self.logger.debug("Received response ode {0} with reason {1}...".format(response.status_code, response.reason))
        self.session.headers.pop("Content-Type")  # Remove header, as it affects other functions
        return response.json()['response']

    def delete_hadoop_data_source(self, name):
        """

        :param name:
        :return:
        """
        data_source_id = self.get_hadoop_data_source_id(name)
        url = "{0}/hdfs_data_sources/{1}".format(self.base_url, data_source_id)
        url = self._add_token_to_url(url)
        self.logger.debug("Deleting data source {0}".format(name))
        response = self.session.delete(url)
        self.logger.debug("Received response code {0} with reason {1}".format(response.status_code, response.reason))
        return response

    def delete_hadoop_data_source_if_exists(self, name):
        """

        :param name:
        :return:
        """
        try:
            return self.delete_hadoop_data_source(name)
        except DataSourceNotFoundException:
            self.logger.debug("Data source {0} not found, we don't need to delete it".format(name))

    def get_database_list(self, data_source_id, per_page=100):
        database_list = None
        url = "{0}/data_sources/{1}/databases".format(self.base_url, data_source_id)
        url = self._add_token_to_url(url)
        self.logger.debug("Getting list of Database from {0}".format(url))
        page_current = 0
        while True:
            payload = {
                "all": True,
                "per_page": per_page,
                "page": page_current + 1,
            }
            database_list_response = self.session.get(url, params=payload, verify=False).json()
            page_total = database_list_response['pagination']['total']
            page_current = database_list_response['pagination']['page']
            if database_list:
                database_list.extend(database_list_response['response'])
            else:
                database_list = database_list_response['response']
            if page_total == page_current:
                break
        return database_list