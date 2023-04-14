"""
Implement the ArgumentationAgent class.
"""

import random
import pdb

from mesa import Model
from mesa.time import RandomActivation
import numpy as np
from argmas_auto.communication.agent.CommunicatingAgent import CommunicatingAgent
from argmas_auto.communication.message.MessageService import MessageService
from argmas_auto.communication.preferences.Item import Item
from argmas_auto.communication.message.Message import Message
from argmas_auto.communication.message.MessagePerformative import MessagePerformative
from argmas_auto.communication.mailbox.Mailbox import Mailbox
from argmas_auto.arguments.Argument import Argument
from argmas_auto.communication.preferences import Preferences
from argmas_auto.communication.preferences import Value
from argmas_auto.communication.preferences import CriterionName, CriterionValue


class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherits from CommunicatingAgent.
    """

    def __init__(self, unique_id, model, name, dest_name, list_items):
        super().__init__(unique_id, model, name)
        self.name = name
        self.model = model
        self.dest_name = dest_name
        self.conversation_started = {self.dest_name: False}
        self.profile_thresholds = {}
        # will be edited to remove items among which we agree
        self.list_items = list_items
        self.ordered_items = None
        self.prefered_item = None

    def step(self):
        """
        Implement how the Agent evolves through time.

        Note: agents communicate while they disagree, then switch destinary.
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
                    self.prefered_item,
                )
                self.send_message(mess)
            elif (
                messages
                and messages[0].get_performative() == MessagePerformative.ASK_WHY
            ):
                # Alice argues for its proposal
                mess = Message(
                    self.name,
                    self.dest_name,
                    MessagePerformative.ARGUE,
                    "Empty message.",
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
                    messages[0].get_content(),
                )
                self.send_message(mess)
                # remove the accepted item from the list of items
                self.remove_item_from_preferences(messages[0].get_content())
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
                    messages[0].get_content(),
                )
                self.send_message(mess)
                self.remove_item_from_preferences(messages[0].get_content())

    def get_preference(self):
        """
        Return the Agent's prefered choice.
        """
        return self.prefered_item

    def generate_preference_profiles(self, bounds):
        """
        Generate preference profiles.
        """
        for criterion in CriterionName:
            # generate 4 thresholds to distinguish between VERY_BAD, BAD, etc.
            min_value, max_value = bounds[criterion.name]
            random_numbers = [random.randint(min_value, max_value) for i in range(4)]
            self.profile_thresholds[criterion.name] = sorted(random_numbers)

    def generate_preferences(self, criterion_value_list):
        """
        Generate the preference table.
        """
        self.preferences = Preferences()
        # set the name of criterion we use
        self.preferences.set_criterion_name_list([crit.name for crit in CriterionName])
        # add values (***) for each of the criterion and for each item
        for crit_value_pair in criterion_value_list:
            # object CriterionValue where value is a numerical score
            # convert the value from numerical to stars (***)
            item_name = crit_value_pair.get_item()
            crit_name = crit_value_pair.get_criterion_name()
            crit_value = crit_value_pair.get_value()
            thresholds = self.profile_thresholds[crit_name]
            index = 0
            for thresh in thresholds:
                if crit_value > thresh:
                    index += 1
            star_value = Value(index)
            self.preferences.add_criterion_value(
                CriterionValue(item_name, crit_name, star_value)
            )

    def get_preference_among_list_items(self):
        """
        Pick the Agent's prefered choice among a list of items.
        """

        # create the preference profile
        items_scores_mapping = [
            item.get_score(self.preferences) for item in self.list_items
        ]
        self.ordered_items = {
            self.list_items[i]: items_scores_mapping[i]
            for i in range(len(self.list_items))
        }
        best_index = np.argmax(items_scores_mapping)
        self.prefered_item = self.list_items[best_index]

    def is_among_top_items(self, item):
        """
        Return True if item is in the Agent's top 10% items.
        """
        # pdb.set_trace()
        if self.ordered_items is None:
            self.get_preference_among_list_items(self.list_item)
        top_ten_percent_rank = int(len(self.ordered_items) * 0.1) + 1
        top_preferences_object = sorted(self.ordered_items.values, reverse=True)[
            :top_ten_percent_rank
        ]
        top_preferences = [pref.get_description() for pref in top_preferences_object]

        if item in top_preferences:
            return True
        return False

    def remove_item_from_preferences(self, item):
        """
        Remove the item given in argument from the ordered list of items.
        """
        item_name = item.get_name()
        # note: cannot use self.ordered_preferences.remove(item) because the Item objects of
        # Alice and Bob are NOT the same (although identical)

        # delete item from self.list_items
        self.list_items.remove(item)

        # regenerate self.ordered_items and self.prefered_item
        self.get_preference_among_list_items()

    def support_proposal(self, item):
        """
        Used when the agent receives "ASK_WHY" after having proposed an item
        :param item: str - name of the item which was proposed
        :return: string - the strongest supportive argument
        """
        
        argument = Argument()
        premisses_pro_item = argument.list_supporting_proposal(item, self.preferences)
        for prem in premisses_pro_item:
            continue
        return argument.__str__()
