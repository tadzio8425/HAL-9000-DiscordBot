import json
from zoomus import ZoomClient


class ZoomUs:

    def __init__(self):

        self.client = ZoomClient('5NZQxuEvQUaJfOa6a-0pZA', 'YC0yxbuMpSP4P5iyXqgQ1mN6dYqrcwgtdZwZ')

        user_list_response = self.client.user.list()
        self.user_list = json.loads(user_list_response.content)

        for user in self.user_list['users']:
            user_id = user['id']
            self.zoom_info = json.loads(self.client.meeting.list(user_id=user_id).content)
            self.user_id = self.user_list["users"][0]["id"]
            
    
    def create_meeting(self):

        self.client.meeting.create(user_id = self.user_id)

        self.zoom_info = json.loads(self.client.meeting.list(user_id=self.user_id).content)

        meeting_link = self.zoom_info["meetings"][0]["join_url"]

        return meeting_link


    def delete_meeting(self):

        self.zoom_info = json.loads(self.client.meeting.list(user_id=self.user_id).content)

        for meeting in self.zoom_info["meetings"]:

            meeting_id = meeting["id"]

            self.client.meeting.delete(host_id = self.user_id, id = meeting_id)