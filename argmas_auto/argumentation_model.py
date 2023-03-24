import random

from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.Item import Item
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.mailbox.Mailbox import Mailbox


class ArgumentModel(Model):
    """
    ArgumentModel which inherits from Model.
    """

    def __init__(self):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)

        self.list_items = [
            Item("E", "Moteur électrique"),
            Item("ICED", "Moteur à combustion interne Diesel"),
        ]
        self.alice = ArgumentAgent(0, self, "Alice", None)
        self.alice.generate_preferences(self.list_items)
        self.bob = ArgumentAgent(1, self, "Bob", None)
        self.bob.generate_preferences(self.list_items)

        self.schedule.add(self.alice)
        self.schedule.add(self.bob)
        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.schedule.step()
