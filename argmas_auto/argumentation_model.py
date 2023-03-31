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

from argmas_auto.argumentation_agent import ArgumentAgent


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
        self.alice = ArgumentAgent(0, self, "Alice", None, dest_name="Bob")
        self.alice.generate_preferences(self.list_items)
        self.bob = ArgumentAgent(1, self, "Bob", None, dest_name="Alice")
        self.bob.generate_preferences(self.list_items)

        self.schedule.add(self.alice)
        print("[ArgumentModel] Created Agent Alice.")
        self.schedule.add(self.bob)
        print("[ArgumentModel] Created Agent Bob.")
        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        # at this point, one agent should have received a message
        self.schedule.step()
