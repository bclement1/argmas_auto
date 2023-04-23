""" 
Project's entry point.
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

from argmas_auto.argumentation_model import ArgumentModel


if __name__ == "__main__":
    argument_model = ArgumentModel()
    print("[MAIN]: Model created.")
    # disable instant delivery (asynchronous communications)
    MessageService.get_instance().set_instant_delivery(False)

    # run a step
    for i in range(10):
        argument_model.step()
