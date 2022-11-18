# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from email import policy

from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest

from .preparers import CommunicationResourcePreparer
from .recording_processors import BodyReplacerProcessor, URIIdentityReplacer


class CommunicationRoomsScenarios(ScenarioTest):

    def __init__(self, method_name):
        super().__init__(method_name, recording_processors=[
            URIIdentityReplacer(),
            BodyReplacerProcessor(keys=["id"]),
        ])
    
    def __create_rooms(self, communication_resource_info):
        connection_str = communication_resource_info[1]
        if self.is_live or self.in_recording:
            self.kwargs.update({ 'connection_string': connection_str})
        else:
            os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = connection_str
        
        res = self.cmd('az communication rooms create --rooms --participants{participants_id}').get_output._in_json()
        return res['rooms']
        
    def __get_rooms(self, rooms_id):
        self.kwargs.update({
            'roomsId': rooms_id})
        return self.cmd('az communication rooms get --roomId {rooms_id}').get_output_in_json()


    def __create_participants(self,communication_resource_info):     
        connection_str =  communication_resource_info[1]
        # create a new user 
        if self.is_live or self.in_recording:
            self.kwargs.update({
                'connection_string': connection_str})
        else:
            os.environ['AZURE_COMMUNICATION_CONNECTION_STRING'] = connection_str
        
        res = self.cmd('az communication identity token issue --scope room').get_output_in_json()
        return res['participants_id']
    
    def __get_connectionString_from_resource_info(self, communication_resource_info):
        return communication_resource_info[2]
        #what 2 stands for in here?

    def __CommunicationRoomsScenarios_update_environ(self, communication_resource_info):
        communicationString = self.__get_connectionString_from_resource_info(communication_resource_info)
        os.environ['AZURE_COMMUNICATION_STRING'] = communicationString

        return communicationString 

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def test_communication_rooms_create_without_room_join_policy(self, communication_resource_info):
        self.__CommunicationRoomsScenarios_update_environ(communication_resource_info)
        
        room = self.cmd('az communication rooms create').get_output_in_json()
        
        id = room['id']
        participants = room['participants']
        roomJoinPolicy = room['roomJoinPolicy']
        
        assert len(id) > 8 
        assert len (participants) == 0
        assert roomJoinPolicy == 'InviteOnly'

    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def  test_communication_rooms_create_bad_join_policy(self, communication_resource_info):
        
        # add invalid join policy to the rooms
        self.kwargs.update({
            'join_policy': 'azure12345'})
        print(self.kwargs.update)
 
        with self.assertRaises(Exception) as raises:
            self.cmd('az communication rooms create --join-policy {join_policy}', checks = [
                self.check('CommunicationError.code', 'Bad Request')])
        
        print(str(raises.exception))
        assert 'The JSON value could not be converted to Microsoft.AzureCommunicationService.Rooms.Api.Contracts.V2022_02_01.RoomJoinPolicyDto' in str(raises.exception)
    
    @ResourceGroupPreparer(name_prefix='clitestcommunication_MyResourceGroup'[:7], key='rg', parameter_name ='rg')
    @CommunicationResourcePreparer(resource_group_parameter_name='rg')
    def  test_communication_rooms_create_empty_join_policy(self, communication_resource_info):
         
        # add empty join policy to the rooms  
        self.kwargs.update({
                'join_policy': '""'})
        print(self.kwargs.update)

               
        with self.assertRaises(Exception) as raises:
            self.cmd('az communication rooms create --join-policy {join_policy}', checks = [
                self.check('CommunicationError.code', 'Bad Request')])
        
        print(str(raises.exception))
        assert 'The JSON value could not be converted to Microsoft.AzureCommunicationService.Rooms.Api.Contracts.V2022_02_01.RoomJoinPolicyDto' in str(raises.exception)


    
 




        
        

    
       



        

    