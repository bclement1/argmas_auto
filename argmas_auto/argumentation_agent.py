import random

from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.Item import Item
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.mailbox.Mailbox import Mailbox


class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherit from CommunicatingAgent.
    """

    def __init__(self, unique_id, model, name, preferences):
        super().__init__(unique_id, model, name, preferences)
        self.preference = preferences

    def step(self):
        super().step()

    def get_preference(self):
        return self.preference

    def generate_preferences(self, List_items):
        # see question 3
        # To be completed

        self.preference = random.shuffle(List_items)
