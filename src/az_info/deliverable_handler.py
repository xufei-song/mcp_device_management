from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pprint
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

    def get_work_item(self, work_item_id, project='OS'):
        """
        Get work item details by ID
        
        Args:
            work_item_id (int): The ID of the work item to retrieve
            project (str): The project name (default: 'OS')
        
        Returns:
            Work item object with all details
        """
        try:
            work_item = self.work_item_tracking_client.get_work_item(
                id=work_item_id,
                project=project,
                expand='All'  # Include all fields, relations, etc.
            )
            return work_item
        except Exception as e:
            print(f"Error retrieving work item {work_item_id}: {e}")
            return None

    def get_deliverable_info(self, deliverable_id, project='OS'):
        """
        Get deliverable information by ID
        
        Args:
            deliverable_id (int): The ID of the deliverable to retrieve
            project (str): The project name (default: 'OS')
        
        Returns:
            Dictionary with formatted deliverable information
        """
        work_item = self.get_work_item(deliverable_id, project)
        
        if not work_item:
            return None
        
        # Extract key information from the work item
        deliverable_info = {
            'id': work_item.id,
            'title': work_item.fields.get('System.Title', 'N/A'),
            'description': work_item.fields.get('System.Description', 'N/A'),
            'state': work_item.fields.get('System.State', 'N/A'),
            'work_item_type': work_item.fields.get('System.WorkItemType', 'N/A'),
            'created_date': work_item.fields.get('System.CreatedDate', 'N/A'),
            'created_by': work_item.fields.get('System.CreatedBy', {}).get('displayName', 'N/A') if work_item.fields.get('System.CreatedBy') else 'N/A',
            'assigned_to': work_item.fields.get('System.AssignedTo', {}).get('displayName', 'N/A') if work_item.fields.get('System.AssignedTo') else 'N/A',
            'area_path': work_item.fields.get('System.AreaPath', 'N/A'),
            'iteration_path': work_item.fields.get('System.IterationPath', 'N/A'),
            'url': f"https://microsoft.visualstudio.com/OS/_workitems/edit/{work_item.id}",
            'relations': []
        }
        
        # Extract relations if they exist
        if hasattr(work_item, 'relations') and work_item.relations:
            for relation in work_item.relations:
                relation_info = {
                    'rel': relation.rel,
                    'url': relation.url,
                    'attributes': relation.attributes if hasattr(relation, 'attributes') else {}
                }
                deliverable_info['relations'].append(relation_info)
        
        return deliverable_info

    def print_deliverable_info(self, deliverable_info):
        """
        Pretty print deliverable information
        
        Args:
            deliverable_info (dict): Deliverable information dictionary
        """
        if not deliverable_info:
            print("No deliverable information available.")
            return
        
        print("=" * 60)
        print(f"DELIVERABLE INFORMATION")
        print("=" * 60)
        print(f"ID: {deliverable_info['id']}")
        print(f"Title: {deliverable_info['title']}")
        print(f"Type: {deliverable_info['work_item_type']}")
        print(f"State: {deliverable_info['state']}")
        print(f"Created Date: {deliverable_info['created_date']}")
        print(f"Created By: {deliverable_info['created_by']}")
        print(f"Assigned To: {deliverable_info['assigned_to']}")
        print(f"Area Path: {deliverable_info['area_path']}")
        print(f"Iteration Path: {deliverable_info['iteration_path']}")
        print(f"URL: {deliverable_info['url']}")
        print("-" * 60)
        print(f"Description:")
        print(f"{deliverable_info['description']}")
        
        if deliverable_info['relations']:
            print("-" * 60)
            print(f"Relations ({len(deliverable_info['relations'])}):")
            for i, relation in enumerate(deliverable_info['relations'], 1):
                print(f"  {i}. {relation['rel']}")
                print(f"     URL: {relation['url']}")
                if relation['attributes']:
                    print(f"     Attributes: {relation['attributes']}")
        
        print("=" * 60)

    def add_comment_to_deliverable(self, deliverable_id, comment_text, project='OS'):
        """
        Add a comment to the deliverable's Discussion
        
        Args:
            deliverable_id (int): The ID of the deliverable to update
            comment_text (str): The comment text to add
            project (str): The project name (default: 'OS')
        
        Returns:
            Boolean indicating success/failure
        """
        try:
            # Create patch document to add comment
            patch_document = [
                JsonPatchOperation(
                    op='add',
                    path='/fields/System.History',
                    value=comment_text
                )
            ]
            
            # Update the work item with the comment
            updated_work_item = self.work_item_tracking_client.update_work_item(
                document=patch_document,
                id=deliverable_id,
                project=project
            )
            
            print(f"[SUCCESS] Comment added to deliverable {deliverable_id}")
            print(f"Comment: {comment_text}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to add comment to deliverable {deliverable_id}: {e}")
            return False

    def update_deliverable_with_comment(self, deliverable_id, comment_text, project='OS'):
        """
        Update deliverable and add comment in Discussion
        
        Args:
            deliverable_id (int): The ID of the deliverable to update
            comment_text (str): The comment text to add to Discussion
            project (str): The project name (default: 'OS')
        
        Returns:
            Boolean indicating success/failure
        """
        print(f"[INFO] Updating deliverable {deliverable_id} with comment...")
        
        # First, verify the deliverable exists
        work_item = self.get_work_item(deliverable_id, project)
        if not work_item:
            print(f"[ERROR] Deliverable {deliverable_id} not found")
            return False
        
        print(f"[INFO] Found deliverable: {work_item.fields.get('System.Title', 'N/A')}")
        
        # Add comment to Discussion
        success = self.add_comment_to_deliverable(deliverable_id, comment_text, project)
        
        if success:
            print(f"[SUCCESS] Successfully updated deliverable {deliverable_id}")
            print(f"[INFO] View deliverable at: https://microsoft.visualstudio.com/OS/_workitems/edit/{deliverable_id}")
        
        return success