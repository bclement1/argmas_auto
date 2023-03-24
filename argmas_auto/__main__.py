""" 
Project's entry point.
"""

import random

from mesa import Model
from mesa.time import RandomActivation

from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.MessageService import MessageService
from communication.preferences.Item import Item
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.mailbox.Mailbox import Mailbox


if __name__ == " __main__ ":
    argument_model = ArgumentModel()
    mailbox = Mailbox()
    item = argument_model.alice.preferences[1]
    m1 = Message(
        argument_model.alice.name,
        argument_model.bob.name,
        MessagePerformative.PROPOSE,
        item,
    )
    m2 = Message(
        argument_model.bob.name,
        argument_model.alice.name,
        MessagePerformative.ACCEPT,
        item,
    )
