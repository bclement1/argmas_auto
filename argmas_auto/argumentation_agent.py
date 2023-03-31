"""
Implement the ArgumentationAgent class.
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


class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherits from CommunicatingAgent.
    """

    def __init__(self, unique_id, model, name, preferences, dest_name):
        super().__init__(unique_id, model, name)
        self.possible_preferences = preferences
        self.name = name
        self.model = model
        self.dest_name = dest_name
        self.ordered_preferences = None  # liste ordonnée des préférences
        self.preference = None  # la top préférence
        self.conversation_started = {self.dest_name: False}

    def step(self):
        """
        Implement how the Agent evolves through time.

        Note : les deux agents communiquent entre eux tant qu'ils ne sont pas d'accord puis ensuite échangent de destinataire.
        """
        super().step()
        if self.name == "Alice":
            # Alice reads the message she received
            messages = self.get_new_messages()
            if messages:
                print(f"{self.name} received: {messages[0]}")
            if not messages and not self.conversation_started[self.dest_name]:
                print(f"{self.name} initiating the conversation.")
                self.conversation_started[self.dest_name] = True
                # propose an item
                mess = Message(
                    self.name,
                    self.dest_name,
                    MessagePerformative.PROPOSE,
                    self.preference,
                )
                self.send_message(mess)
            elif (
                messages
                and messages[0].get_performative() == MessagePerformative.ACCEPT
            ):
                # Bob accepted the item, Alice terminates the conversation
                mess = Message(
                    self.name,
                    self.dest_name,
                    MessagePerformative.COMMIT,
                    "Terminate",
                )
                self.send_message(mess)
        if self.name == "Bob":
            messages = self.get_new_messages()
            if messages:
                print(f"{self.name} received: {messages[0]}")
            if (
                messages
                and messages[0].get_performative() == MessagePerformative.PROPOSE
            ):
                if self.is_among_top_items(messages[0].get_content()):
                    # item proposed in the top 10% of Bob
                    mess = Message(
                        self.name,
                        self.dest_name,
                        MessagePerformative.ACCEPT,
                        messages[0].get_content(),
                    )
                    self.send_message(mess)
                else:
                    # item is not among Agent's favorites: send ASK_WHY
                    mess = Message(
                        self.name,
                        self.dest_name,
                        MessagePerformative.ASK_WHY,
                        messages[0].get_content(),
                    )
                    self.send_message(mess)
            elif (
                messages
                and messages[0].get_performative() == MessagePerformative.COMMIT
            ):
                # Bob knows that Alice terminates and terminates himself
                mess = Message(
                    self.name,
                    self.dest_name,
                    MessagePerformative.COMMIT,
                    "Terminate",
                )
                self.send_message(mess)

    def get_preference(self):
        """
        Return the Agent's prefered choice.
        """
        return self.preference

    def generate_preferences(self, list_items: list):
        """
        Pick the Agent's prefered choice among a list of items.
        """
        random.shuffle(list_items)
        self.ordered_preferences = list_items
        # print(list_items)
        # print(self.ordered_preference)
        self.preference = list_items.pop()

    def is_among_top_items(self, item):
        """
        Return True if item is in the Agent's top 10% items.
        """
        # import pdb

        # pdb.set_trace()
        top_ten_percent_rank = int(len(self.ordered_preferences) * 0.1) + 1
        top_preferences = self.ordered_preferences[:top_ten_percent_rank]
        print(top_preferences)
        if item in top_preferences:
            return True
        else:
            return False
