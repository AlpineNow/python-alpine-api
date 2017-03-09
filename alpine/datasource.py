from .alpineobject import *
from .exception import *


class DataSource(AlpineObject):
    """
    A class for interacting with data sources. These methods may require a login as a user with admin privileges.
    """

    @property
    def dsType(self):
        return self.DSType()

    def __init__(self, base_url=None, session=None, token=None):
        super(DataSource, self).__init__(base_url, session, token)

    def get_list(self, type=None, per_page=100):
        """
        Get a list of metadata for all data sources.

        :param str type: Type of the data source. Select "Database", "Hadoop", or None for both types.
        :param int per_page: Maximum number to fetch with each API call.
        :return: List of data source's metadata.
        :rtype: list of dict

        Example::

            >>> all_datasources = session.datasource.get_list()
            >>> all_database_datasources = session.datasource.get_list(type = "Database")
            >>> all_hadoop_datasources = session.datasource.get_list(type = "Hadoop")
            >>> len(all_datasources)
            20

        """
        db_datasource_list = None
        hd_datasource_list = None
        if not type == "Hadoop":
            try:
                url = "{0}/data_sources".format(self.base_url)
                url = self._add_token_to_url(url)
                self.logger.debug("Getting list of {0} data sources from {1}".format("database", url))
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
                    if db_datasource_list:
                        db_datasource_list.extend(datasource_list_response['response'])
                    else:
                        db_datasource_list = datasource_list_response['response']
                    if page_total == page_current:
                        break
            except Exception as ex:
                self.logger.warn("Failed to get {0} data sources, the error is: {1}".format("database", ex.message))
        if not type == "Database":
            try:
                url = "{0}/hdfs_data_sources".format(self.base_url)
                url = self._add_token_to_url(url)
                self.logger.debug("Getting list of {0} data sources from {1}".format("Hadoop", url))
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
                    if hd_datasource_list:
                        hd_datasource_list.extend(datasource_list_response['response'])
                    else:
                        hd_datasource_list = datasource_list_response['response']
                    if page_total == page_current:
                        break
            except Exception as ex:
                self.logger.warn("Failed to get {0} data sources, the error is: {1}".format("Hadoop", ex.message))

        if type is None:
            return db_datasource_list + hd_datasource_list
        elif type == "Database":
            return db_datasource_list
        elif type == "Hadoop":
            return hd_datasource_list
        else:
            return None

    def get(self, ds_id, type):
        """
        Get one data source's metadata.

        :param int ds_id: A unique ID number of the data source.
        :param str type: Data source type. Either "Database" or "Hadoop".
        :return: One data source's metadata.
        :rtype: dict
        :exception DataSourceNotFoundException: the data source does not exist.

        Example::

            >>> session.datasource.get(ds_id = 1, type = "Database")

        """

        if type == "Database":
            url = "{0}/data_sources/{1}".format(self.base_url, ds_id)
        elif type == "Hadoop":
            url = "{0}/hdfs_data_sources/{1}".format(self.base_url, ds_id)
        else:
            raise Exception("the data source type should be either {0} or {1}."
                            .format("Database", "Hadoop")
                            )
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-DSType") is not None:
            self.session.headers.pop("Content-DSType")

        r = self.session.get(url, verify=False)
        ds_response = r.json()

        try:
            if ds_response['response']:
                self.logger.debug("Found {0} data source with ID: <{1}>".format(type, ds_id))
                return ds_response['response']
            else:
                raise DataSourceNotFoundException("{0} data source ID: <{1}> not found".format(type, ds_id))
        except Exception as err:
            raise DataSourceNotFoundException("{0} data source ID: <{1}> not found".format(type, ds_id))

    def get_id(self, name, type=None):
        """
        Gets the ID number of the data source. Will throw an exception if the data source does not exist.

        :param str name: Data source name.
        :param str type: Data source type. Choose to search by "Database" or "Hadoop. Entering None searches both types.
        :return: ID number of the data source
        :rtype: int
        :exception DataSourceNotFoundException: The data source does not exist.

        Example::

            >>> data_source_id = session.datasource.get_id(name = "Demo_GP", type = "Database")
            >>> print(data_source_id)
            786

        """
        ds_list = self.get_list(type)
        for ds_info in ds_list:
            if ds_info['name'] == name:
                return ds_info['id']
        raise DataSourceNotFoundException("Data source with ID: <{0}> and type: <{1}> not found".format(name, type))

    def get_database_list(self, data_source_id, per_page=100):
        """
        Return a list of metadata for all databases in a data source.

        :param int data_source_id: ID number of the data source.
        :param int per_page: Maximum number to fetch with each API call.
        :return: List of database metadata.
        :rtype: list of dict

        Example::

            >>> database_list = session.datasource.get_database_list(data_source_id = 1)
            >>> len(database_list)
            3

        """
        database_list = None
        url = "{0}/data_sources/{1}/databases".format(self.base_url, data_source_id)
        url = self._add_token_to_url(url)
        self.logger.debug("Getting list of databases from {0}".format(url))
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

    class DSType(object):
        """
        Convenience strings for data source types.
        """
        GreenplumDatabase = "gpdb_data_source"
        PostgreSQLDatabase = "pg_data_source"
        OracleDatabase = "oracle_data_source"
        HAWQ = "hawq_data_source"
        JDBCDataSource = "jdbc_data_source"
        JDBCHiveDataSource = "jdbc_hive_data_source"
        HadoopCluster = "hdfs_data_source"
        HadoopHive = "hdfs_hive_data_source"
