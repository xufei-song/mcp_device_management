from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
# pip show azure-devops to check your version,
# TODO improve with virtual env of python
from azure.devops.v7_1.work_item_tracking.models import JsonPatchOperation

class AzureDevOpsClient:
    def __init__(self, personal_access_token):
        self.organization_url = 'https://microsoft.visualstudio.com/'
        self.credentials = BasicAuthentication('', personal_access_token)
        self.connection = Connection(base_url=self.organization_url, creds=self.credentials)
        self.work_item_tracking_client = self.connection.clients.get_work_item_tracking_client()
        # Get a client (the "core" client provides access to projects, teams, etc)
        self.core_client = self.connection.clients.get_core_client()

    def create_deliverable_with_parent(self, title, description, parent_url):
        patch_document = [
            JsonPatchOperation(
                op='add',
                path='/fields/System.Title',
                value=title
            ),
            JsonPatchOperation(
                op='add',
                path='/fields/System.Description',
                value=description
            ),
            JsonPatchOperation(
                op='add',
                path='/relations/-',
                value={
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": parent_url,
                    "attributes": {
                        "comment": "Making a new deliverable a child of the scenario"
                    }
                }
            )
        ]
        print(f"--w-----------ddddd----")

        get_projects_response = self.core_client.get_projects()
        index = 0
        while get_projects_response is not None:
            for project in get_projects_response.value:
                pprint.pprint("[" + str(index) + "] " + project.name)
                index += 1
            if get_projects_response.continuation_token is not None and get_projects_response.continuation_token != "":
                # Get the next page of projects
                get_projects_response = self.core_client.get_projects(continuation_token=get_projects_response.continuation_token)
            else:
                # All projects have been retrieved
                get_projects_response = None
        print(f"--w-----------ddddeeeed----")
        work_item = self.work_item_tracking_client.create_work_item(
            document=patch_document,
            project='OS',
            type='Deliverable'
        )

        print(f"Created work item with ID: {work_item.id}")