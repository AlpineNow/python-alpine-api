from api.exception import *
from api.alpineobject import AlpineObject


class DataSource(AlpineObject):
    """
        A class for interacting with data sources.
        """
    def __init__(self, base_url=None, session=None, token = None):
        super(DataSource, self).__init__(base_url, session, token)
        self.dsType = self.DSType()

    def get_list(self, type=None, per_page=100):
        """
        Get a list of all data sources' metadata
        :param str type: Type of the data source, could be either "Database" or "Hadoop"
        :param int per_page: How many data sources to return in each page.
        :return: A list of all the data sources' data
        rtype: list of dict

        Example::

                    >>> all_datasource = session.datasource.get_list()
                    >>> all_database_datasource = session.datasource.get_list("Database")
                    >>> all_hadoop_datasource = session.datasource.get_list("Hadoop")
                    >>> len(all_datasource)
                    20
        """
        db_datasource_list = None
        hd_datasource_list = None
        if not type == "Hadoop":
            try:
                url = "{0}/data_sources".format(self.base_url)
                url = self._add_token_to_url(url)
                self.logger.debug("Getting list of {0} data sources from {1}".format("Database", url))
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
                self.logger.warn("Fail to get {0} data sources, the error is: {1}".format("Database", ex.message))
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
                self.logger.warn("Fail to get {0} data sources, the error is: {1}".format("Hadoop", ex.message))

        if type == None:
            return db_datasource_list + hd_datasource_list
        elif type == "Database":
            return db_datasource_list
        elif type =="Hadoop":
            return hd_datasource_list
        else:
            return None



        return datasource_list

    def get(self, ds_id, type=None):
        """
        Get one data source's metadata.
        :param str ds_id: A unique id of the data source
        :param str type: Data source type, Could be either "Database" or "Hadoop", None for All
        :return: single data source data
        :rtype dict
        :exception DataSourceNotFoundException: the data source does not exist.
        Example::

                    >>> session.datasource.get(ds_id = 1, type="Database")
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
                self.logger.debug("Found {0} Datasource with id: <{1}>".format(data_source_type, ds_id))
                return ds_response['response']
            else:
                raise DataSourceNotFoundException("{0} Datasource id: <{1}> not found".format(data_source_type, ds_id))
        except Exception as err:
            raise DataSourceNotFoundException("{0} Datasource id: <{1}> not found".format(data_source_type, ds_id))

    def get_id(self, name, type=None):
        """
        Gets the ID number of the data source. Will throw an exception if the data source does not exist.
        :param str name: Data source name
        :param type: Data source Type. None for query all data source type
        :return: ID number of the data source
        :rtype: int
        :exception DataSourceNotFoundException: the data source does not exist
        Example

                    >>> data_source_id = session.datasource.get_id(name = 'demo_data_source', type = "Database")
                    >>> print(data_source_id)
                    16
        """
        ds_list = self.get_list(type)
        for ds_info in ds_list:
            if ds_info['name'] == name:
                return ds_info['id']
        # return None
        raise DataSourceNotFoundException("Datasource with id: <{0}> and type: <{1}>not found".format(name, type))

    def get_database_list(self, data_source_id, per_page=100):
        """
        Get a list of all databases' metadata
        :param str data_source_id: Id of the data source
        :param int per_page: How many data sources to return in each page.
        :return: A list of all the databases' data
        rtype: list of dict

        Example::

                    >>> database_list = session.datasource.get_database_list(1)
                    >>> len(database_list)
                    3
        """
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

    class DSType(object):
        """
        """
        def __init__(self):
            self.GreenplumDatabase = "gpdb_data_source"
            self.PostgreSQLDatabase = "pg_data_source"
            self.OracleDatabase = "oracle_data_source"
            self.HAWQ = "hawq_data_source"
            self.JDBCDataSource = "jdbc_data_source"
            self.JDBCHiveDataSource = "jdbc_hive_data_source"
            self.HadoopCluster = "hdfs_data_source"
            self.HadoopHive = "hdfs_hive_data_source"