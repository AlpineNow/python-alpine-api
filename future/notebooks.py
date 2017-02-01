# TODO Not finished yet

"""Notebooks"""


def run_notebook(self, workspace_id, user_id, payload, command_to_execute):
    # e.g. notebook_url = "http://10.10.0.199:8000/api/v1.0/run_notebook_in_docker"
    notebook_url = "{0}/v1.0/{1}".format(self.base_url, command_to_execute)
    url = self._add_token_to_url(notebook_url)
    response = self.session.post(url, data=payload, verify=False)

    return response

    # put together the path for creating notebook directory with user_id like chorus_notebook.tmp.user_id
    path_for_creating_notebook_user_dir = self.home_dir + '/' + "notebook/notebook_data/chorus_notebook.tmp." + str(
        user_id)
    cmd = "su - chorus -c 'mkdir {0} && ls -l' 2>&1".format(path_for_creating_notebook_user_dir)
    results = self.utils.execute_remote_shell_command(self.host, 'root', 'alpineRocks', cmd)

    if not results:
        raise FailedtoCreateEntityException(
            "Failed to create path_for_creating_notebook_user_dir {0}.".format(path_for_creating_notebook_user_dir))

    # put together the path for creating workspace directory inside chorus_notebook.tmp.user_id
    notebook_workspace_dir = self.home_dir + '/' + "notebook/notebook_data/chorus_notebook.tmp." + str(
        user_id) + '/' + str(workspace_id)
    cmd = "su - chorus -c 'mkdir {0} && ls -l' 2>&1".format(notebook_workspace_dir)
    results = self.utils.execute_remote_shell_command(self.host, 'root', 'alpineRocks', cmd)
    if not results:
        raise FailedtoCreateEntityException(
            "Failed to create notebook_workspace_dir {0}.".format(notebook_workspace_dir))

    workfile_versions_dir = self.utils.chorus_data_dir + "/system/workfile_versions/"
    cmd = "su - chorus -c 'cd {0} && ls -1tr | tail -1' 2>&1".format(workfile_versions_dir)
    results = self.utils.execute_remote_shell_command(self.host, 'root', 'alpineRocks', cmd)
    if not results:
        raise Exception("Failed to get the directory {0}.".format(path_for_creating_notebook_user_dir))

    original_workfile_versions_dir = workfile_versions_dir + results[0].rstrip("\r\n") + '/' + 'original/'
    path_of_uploaded_file = original_workfile_versions_dir + notebook_file

    cmd = "su - chorus -c 'cp %s %s'" % (path_of_uploaded_file, notebook_workspace_dir)
    results = self.utils.execute_remote_shell_command(self.host, 'root', 'alpineRocks', cmd)

    # put together the path where the ipynb file will be run in docker container
    docker_ipynb_file_path = "/home/chorus/ChorusCommander/" + "chorus_notebook.tmp." + str(user_id) + '/' + str(
        workspace_id) + '/' + notebook_file

    # preparing to run the file
    payload = {'username': user_id, 'chorus_address': chorus_address[:-4],
               "command": "pip install runipy && runipy -o %s && jupyter notebook --config=chorus_notebook_config.py" % docker_ipynb_file_path}
    command_to_execute = "run_notebook_in_docker"
    response = self.workfile_api.run_notebook(self.token, self.chorus_address, self.notebook_address, payload,
                                              command_to_execute)
    if response.status_code != 201:
        raise Exception("Notebook FAILED to run").format(response.status_code)

    # check if a container was launched.
    payload_check_result = {'username': user_id}

    command_to_execute = "get_container_for_user"
    response = self.workfile_api.get_notebook_container_response(self.token, self.chorus_address, self.notebook_address,
                                                                 payload_check_result, command_to_execute)

    if response.status_code != 200:
        raise Exception("Notebook failed to run with status code {0}".format(response.status_code))


def stop_notebook_containers(self, notebook_address):
    """
    This function will stop all the docker containers.
    :param token:
    :param chorus_address:
    :param notebook_address:
    :return:
    """
    notebook_session = requests.session()
    notebook_url = notebook_address + "/v1.0/" + "stop_all_notebook_docker_container"
    logger.info("notebook_url {0}".format(notebook_url))
    payload = {'prefix': "chorus_notebook.tmp."}
    response = notebook_session.post(notebook_url, data=payload)
    logger.info("response {0}".format(response))

    return response


def get_notebook_container_response(self, notebook_address, payload, command_to_execute):
    """

    :param token:
    :param chorus_address:
    :param notebook_address:
    :param payload:
    :param command_to_execute:
    :return:
    """
    notebook_session = requests.session()

    notebook_url_check_result = notebook_address + "/v1.0/" + command_to_execute
    # notebook_url_check_result = "http://10.10.0.199:8000/api/v1.0/get_container_for_user"
    logger.info("notebook_url_check_result {0}".format(notebook_url_check_result))
    response = notebook_session.get(notebook_url_check_result, params=payload)
    logger.info("response from run {0}".format(response))

    return response


def upload_notebook(self, workspace_id, notebook_file):
    """

    :param workspace_id:
    :param notebook_file:
    :return:
    """
    # Set the URL for uploading the workfiles
    url = "{0}/workspaces/{1}/workfiles".format(self.base_url, workspace_id)
    url = self._add_token_to_url(url)

    payload = {"data_source": "",
               "database": "",
               "workfile[entity_subtype]": "",
               "workfile[execution_locations][0][entity_type]": "",
               }
    # files is used to create a multipart upload content-type with requests, we send in a file object
    self.logger.debug("payload for upload {0}".format(payload))
    files = {"workfile[versions_attributes][0][contents]": open(notebook_file, 'rb')}

    self.logger.info("notebook_file = {0}".format(notebook_file))
    # upload notebook
    response = self._post_session(url, payload, files=None, verify=False)

    return response


def create_new_notebook(self, workflow_name):
    pass


def create_new_link(self, workflow_name):
    pass


def create_new_sql_file(self, workflow_name):
    pass


def update_workfile(self):
    pass