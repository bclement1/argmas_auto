""" 
Implement the ArgumentationModel class.
"""

import random

from mesa import Model
from mesa.time import RandomActivation

from argmas_auto.communication.agent.CommunicatingAgent import CommunicatingAgent
from argmas_auto.communication.message.MessageService import MessageService
from argmas_auto.communication.preferences.Item import Item
from argmas_auto.communication.message.Message import Message
from argmas_auto.communication.message.MessagePerformative import MessagePerformative
from argmas_auto.communication.mailbox.Mailbox import Mailbox
from argmas_auto.communication.preferences.CriterionValue import CriterionValue
from argmas_auto.communication.preferences.Preferences import Preferences
from argmas_auto.argumentation_agent import ArgumentAgent


CRITERION_BOUNDS = {
    "PRODUCTION_COST": [1, 100],
    "CONSUMPTION": [1, 10],
    "DURABILITY": [1, 25],
    "ENVIRONMENT_IMPACT": [1, 25],
    "NOISE": [1, 10],
}


class ArgumentModel(Model):
    """
    ArgumentModel which inherits from Mesa's Model class.
    """

    def __init__(self):
        super().__init__()
        # initiate the scheduler
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)

        self.list_items = [
            Item("E", "Moteur électrique"),
            Item("ICED", "Moteur à combustion interne Diesel"),
            Item("HAD", "Moteur à hadrons"),
            Item("TB", "Turbo Booster"),
            Item("MTB", "Méga-Turbo Booster"),
            Item("MS", "Moteur supra-luminique"),
            Item("CPE", "Cow-propulsed engine"),
            Item("FCE", "Faucon Millenium engine"),
            Item("TIME", "Mot'heure"),
            Item("HATX", "Hyperpropulseur ATX-5"),
            Item("AVAT", "Hyperpropulseur AVATAR-10"),
            Item("ION", "Moteur ionique P-s6"),
            Item("IONP", "Moteur ionique P-s7, version améliorée du P-s6"),
            Item("STEL", "Moteur stellaire"),
            Item("GRAV", "Moteur à gravité inversée"),
            Item("RHYD", "Moteur à rhydonium"),
        ]

        for item in self.list_items:
            # fill the criterion score table at random for each Item
            item.make_criterion_score_table(CRITERION_BOUNDS)

        # populate CriterionValue objects
        criterion_value_list = []
        for item in self.list_items:
            for crit, value in item.criterion_scores.items():
                criterion_value_list.append(CriterionValue(item, crit, value))

        self.alice = ArgumentAgent(
            0,
            self,
            "You",
            dest_name="Luke",
            preferences=Preferences(),
            list_items=self.list_items.copy(),
        )
        self.alice.generate_preference_profiles(CRITERION_BOUNDS)
        self.alice.generate_preferences(criterion_value_list)
        self.bob = ArgumentAgent(
            1,
            self,
            "Luke",
            dest_name="You",
            preferences=Preferences(),
            list_items=self.list_items.copy(),
        )
        self.bob.generate_preference_profiles(CRITERION_BOUNDS)
        self.bob.generate_preferences(criterion_value_list)
        self.schedule.add(self.alice)
        print("[ArgumentModel] Created Agent You.")
        your_top_engines = [
            item.get_description()
            for item in self.list_items
            if self.alice.preferences.is_item_among_top_10_percent(
                item, self.list_items
            )
        ]
        print(f"Your short-list of engines is: {your_top_engines}")
        self.schedule.add(self.bob)
        print("[ArgumentModel] Created Agent Luke Skywalker (TA TA TADADA).")
        luke_top_engines = [
            item.get_description()
            for item in self.list_items
            if self.bob.preferences.is_item_among_top_10_percent(item, self.list_items)
        ]
        print(f"Luke's short-list of engines is: {luke_top_engines}")
        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        # at this point, one agent should have received a message
        self.schedule.step()
