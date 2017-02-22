import time
import json
from urlparse import urljoin
from urlparse import urlparse
from api.alpineobject import AlpineObject
from api.exception import *
from .workspace import Workspace
from .workflowprocess import WorkflowProcess


class Workfile(AlpineObject):
    """
    A collection of API wrappers and helper methods to interact with Alpine workfiles, including running workflows \
    with or without workflow variables, ...
    """

    process = None

    def __init__(self, base_url, session, token):
        super(Workfile, self).__init__(base_url, session, token)
        self.chorus_domain = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(self.base_url))
        self.logger.debug(self.chorus_domain)
        self.alpine_base_url = urljoin(self.chorus_domain,
                                       "alpinedatalabs/api/{0}/json".format(self._alpine_api_version))
        self.logger.debug("alpine_base_url is: {0}".format(self.alpine_base_url))
        self.process = WorkflowProcess(base_url, session, token)

    def get_list(self, workspace_id, per_page=100):
        """
        Return all workfiles in a workspace.

        :param int workspace_id: Id of workspace.
        :param int per_page: Number of workfiles to get in each call.
        :return: List of workfiles' metadata
        :rtype: list of dict
        :exception WorkspaceNotFoundException: The workspace does not exist.
        """

        workfile_list = None
        url = "{0}/workspaces/{1}/workfiles".format(self.base_url, str(workspace_id))
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")
        page_current = 0
        while True:
            payload = {"no_published_worklets": True,
                       "order": "file_name",
                       "per_page": per_page,
                       "page": page_current + 1,
                       }
            workfile_list_response = self.session.get(url, data=json.dumps(payload), verify=False).json()
            page_total = workfile_list_response['pagination']['total']
            page_current = workfile_list_response['pagination']['page']
            if workfile_list:
                workfile_list.extend(workfile_list_response['response'])
            else:
                workfile_list = workfile_list_response['response']
            if page_total == page_current:
                break
        return workfile_list

    def get(self, workfile_id):
        """
        Return metadata for one workfile in a workspace.

        :param str workfile_id: Id of workfile.
        :return: One workfile's metadata
        :rtype: dict
        :exception WorkspaceNotFoundException: The workspace does not exist.
        :exception WorkfileNotFoundException: The workfile does not exist.
        """

        url = "{0}/workfiles/{1}".format(self.base_url, workfile_id)
        url = self._add_token_to_url(url)

        if self.session.headers.get("Content-Type") is not None:
            self.session.headers.pop("Content-Type")

        r = self.session.get(url, verify=False)
        workfile_response = r.json()

        try:
            if workfile_response['response']:
                self.logger.debug("Found workfile id: <{0}> in list...".format(workfile_id))
                return workfile_response
            else:
                raise WorkfileNotFoundException("Workfile id: <{0}> not found".format(workfile_id))
        except Exception:
            raise WorkfileNotFoundException("Workfile id: <{0}> not found".format(workfile_id))

    def get_id(self, workfile_name, workspace_id):
        """
        Return the ID number of a workfile in a workspace. Mostly used internally.

        :param string workfile_name: Name of workfile.
        :param string workspace_id: Id of workspace that contains the workfile.
        :return: ID number of workfile
        :rtype: int
        :exception WorkspaceNotFoundException: The workspace does not exist.
        :exception WorkfileNotFoundException: The workfile does not exist.
        """

        workfile_list = self.get_list(workspace_id)
        for workfile in workfile_list:
            if workfile['file_name'] == workfile_name:
                return workfile['id']
        # return None
        raise WorkfileNotFoundException("The workfile with name <{0}> is not found in workspace <{1}>"
                                        .format(workfile_name, workspace_id))

    def delete(self, workfile_id):
        """
        Delete a workfile from a workspace.

        :param workfile_id: Name of workfile to delete.
        :return: None
        :rtype: NoneType
        :exception WorkspaceNotFoundException: The workspace does not exist.
        :exception WorkfileNotFoundException: The workfile does not exist.
        """
        try:
            self.get(workfile_id)
            # Construct the URL
            url = "{0}/workfiles/{1}".format(self.base_url, workfile_id)
            url = self._add_token_to_url(url)
            self.logger.debug("We have constructed the URL and the URL is {0}...".format(url))

            # POSTing a HTTP DELETE
            self.logger.debug("Deleting the workfile with id: <{0}>".format(workfile_id))
            response = self.session.delete(url, verify=False)
            self.logger.debug(
                "Received response code {0} with reason {1}...".format(response.status_code, response.reason))
            if response.status_code == 200:
                self.logger.debug("Workfile successfully deleted.")
            else:
                raise InvalidResponseCodeException("Response Code Invalid, the expected Response Code is {0}, "
                                                   "the actual Response Code is {1}".format(200, response.status_code))
            return None
        except WorkfileNotFoundException as err:
            self.logger.debug("Workfile not found, error {}".format(err))

    def upload(self, workspace_id, afm_file, data_source_id):
        pass

    def upload_hdfs_afm(self, workspace_id, data_source_id, afm_file):
        """

        :param workspace_id:
        :param data_source_id:
        :param afm_file:
        :return:
        """
        url = "{0}/workspaces/{1}/workfiles".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        try:
            self.session.headers.pop("Content-Type")  # Remove header
        except:
            pass
        # payload is made up of file / destination meta-data (see firebug POST trace for info)
        payload = {"data_source": "{0}HdfsDataSource".format(data_source_id),
                   "workfile[entity_subtype]": "alpine",
                   "workfile[execution_locations][0][entity_type]": "hdfs_data_source",
                   "workfile[execution_locations][0][id]": data_source_id}
        # files is used to create a multipart upload content-type with requests, we send in a file object
        files = {"workfile[versions_attributes][0][contents]": open(afm_file, 'rb')}
        self.logger.debug("POSTing to: {0}\n With payload: {1}".format(url, payload))
        response = self.session.post(url, files=files, data=payload, verify=False)
        return response.json()['response']

    def upload_db_afm(self, workspace_id, data_source_id, database_id, datasource_type, database_type,
                      afm_file):
        """
        Uploads a DB afm file for execution
        :param workspace_id:
        :param data_source_id:
        :param database_id:
        :param datasource_type:
        :param database_type:
        :param afm_file:
        :return:
        """
        url = "{0}/workspaces/{1}/workfiles".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        try:
            self.session.headers.pop("Content-Type")  # Remove header
        except:
            pass
        payload = {"data_source": str(data_source_id) + datasource_type,
                   "database": database_id,
                   "workfile[entity_subtype]": "alpine",
                   "workfile[execution_locations][0][entity_type]": database_type,
                   "workfile[execution_locations][0][id]": database_id}
        # files is used to create a multipart upload content-type with requests, we send in a file object
        files = {"workfile[versions_attributes][0][contents]": open(afm_file, 'rb')}
        self.logger.debug("POSTing to: {0}\n With payload: {1}".format(url, payload))
        response = self.session.post(url, files=files, data=payload, verify=False)
        return response.json()['response']

    def upload_hdfs_and_db_afm(self, workspace_id, hdfs_datasource_id,
                               db_datasource_id, db_datasource_type, database_id, database_type, afm_file):
        """
        Uploads an afm with both a hdfs and a db data source.
        :param token: session_id
        :param chorus_address: the root url
        :param workspace_name: the workspace where the afm will be uploaded
        :param hdfs_datasource_name: the hdfs data source
        :param database_datasource_name: the db data source
        :param database_name: the database within the the db data source
        :param afm_file: work file name.
        :return:
        """
        url = "{0}/workspaces/{1}/workfiles".format(self.base_url, workspace_id)
        url = self._add_token_to_url(url)
        payload = [("data_source", str(hdfs_datasource_id) + "HdfsDataSource"),
                   ("database", ''),
                   ("data_source", str(database_id) + db_datasource_type),
                   ("database", database_id),
                   ("workfile[entity_subtype]", "alpine"),
                   ("workfile[execution_locations][0][entity_type]", 'hdfs_data_source'),
                   ("workfile[execution_locations][0][id]", hdfs_datasource_id),
                   ("workfile[execution_locations][1][entity_type]", database_type),
                   ("workfile[execution_locations][1][id]", database_id )]
        files = {"workfile[versions_attributes][0][contents]": open(afm_file, 'rb')}
        response = self._post_afm(url, files, payload)
        return response
