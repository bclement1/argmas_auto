""" 
Project's entry point.
"""
import time
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

TIMEOUT = 60

if __name__ == "__main__":
    argument_model = ArgumentModel()
    print("[MAIN]: Model created.")
    # disable instant delivery (asynchronous communications)
    MessageService.get_instance().set_instant_delivery(False)

    # run a step
    start_time = time.time()
    end_time = time.time()
    print("Luke and You have " + str(TIMEOUT) + " seconds to debate.")
    while (end_time - start_time < TIMEOUT) and argument_model.running:
        argument_model.step()
        end_time = time.time()
    if not argument_model.running:
        print("You and Luke repare the X-wing and leave Tatooine.")
    else:
        print("Too late, the Empire caught You and Luke.")
