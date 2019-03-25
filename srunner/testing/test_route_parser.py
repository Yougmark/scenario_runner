import unittest
import os
from pprint import pprint
#import torch

#from configs import g_conf, set_type_of_process, merge_with_yaml
#from input import RandomSequenceSampler, RandomSampler
#from utils.general import create_log_folder, create_exp_path


import srunner.challenge.utils.route_configuration_parser as parser
from srunner.challenge.challenge_evaluator_routes import ChallengeEvaluator

from srunner.scenariomanager.carla_data_provider import CarlaActorPool

from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.challenge.utils.route_manipulation import interpolate_trajectory
import carla


"""
The idea of this test is to check if sampling is able to sample random sequencial images
inside a batch

"""



class Arguments():

    def __init__(self):
        self.agent = None
        self.use_docker = False
        self.host = '127.0.0.1'
        self.port = 2000
        self.split = 'dev_track_1'


class TestRouteGenerator(unittest.TestCase):

    def __init__(self, name='runTest'):
        unittest.TestCase.__init__(self, name)
        self.root_route_file_position = 'srunner/challenge/'


    def test_route_parser(self):

        args = Arguments()
        client = carla.Client(args.host, int(args.port))
        client.set_timeout(25.0)
        challenge = ChallengeEvaluator(args)

        filename = os.path.join(self.root_route_file_position, 'all_towns_traffic_scenarios.json')
        world_annotations = parser.parse_annotations_file(filename)
        # retrieve routes
        # Which type of file is expected ????

        filename = os.path.join(self.root_route_file_position, 'routes_training.xml')
        list_route_descriptions = parser.parse_routes_file(filename)

        # For each of the routes to be evaluated.
        for route_description in list_route_descriptions:
            #route_description = list_route_descriptions[0]

            challenge.world = client.load_world(route_description['town_name'])

            # Set the actor pool so the scenarios can prepare themselves when needed
            CarlaActorPool.set_world(challenge.world)

            CarlaDataProvider.set_world(challenge.world)
            # find and filter potential scenarios
            # Returns the iterpolation in a different format

            challenge.world.wait_for_tick()
            gps_route, route_description['trajectory'] = interpolate_trajectory(challenge.world,
                                                                                route_description['trajectory'])


            potential_scenarios_definitions, existent_triggers = parser.scan_route_for_scenarios(route_description,
                                                                                                 world_annotations)

            for trigger_id, possible_scenarios in potential_scenarios_definitions.items():

                print ("For trigger ", trigger_id, " --  ", possible_scenarios[0]['trigger_position'])
                for scenario in possible_scenarios:
                    print ("     ", scenario['name'])

            challenge.cleanup(ego=True)