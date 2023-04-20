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
from argmas_auto.arguments.Argument import Argument
from argmas_auto.communication.preferences import Preferences
from argmas_auto.communication.preferences import Value
from argmas_auto.communication.preferences import CriterionName, CriterionValue


class ArgumentAgent(CommunicatingAgent):
    """
    ArgumentAgent which inherits from CommunicatingAgent.
    """

    def __init__(
        self,
        unique_id,
        model,
        name,
        dest_name,
        preferences: Preferences,
        list_items: list,
    ):
        super().__init__(unique_id, model, name)
        self.name = name
        self.model = model
        self.dest_name = dest_name
        self.conversation_started = {self.dest_name: False}
        self.profile_thresholds = {}
        # will be edited to remove items among which we agree
        self.preferences = preferences
        self.list_items = list_items
        self.preferred_item = None

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
                self.preferred_item = self.preferences.most_preferred(self.list_items)
                mess = Message(
                    self.name,
                    self.dest_name,
                    MessagePerformative.PROPOSE,
                    self.preferred_item,
                )
                self.send_message(mess)
            elif (
                messages
                and messages[0].get_performative() == MessagePerformative.ASK_WHY
            ):
                # Alice argues for its proposal
                best_argument = self.support_proposal(self.preferred_item)
                mess = Message(
                    self.name,
                    self.dest_name,
                    MessagePerformative.ARGUE,
                    best_argument,
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
                self.list_items.remove(self.preferred_item)

        if self.name == "Bob":
            messages = self.get_new_messages()
            if messages:
                print(f"{self.name} received: {messages[0]}")
            if (
                messages
                and messages[0].get_performative() == MessagePerformative.PROPOSE
            ):
                if self.preferences.is_among_top_10_percent(
                    item=messages[0].get_content(), item_list=self.list_items
                ):
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
                self.list_items.remove(messages[0].get_content())

    def get_preferences(self):
        """
        Return the Agent's prefered choice.
        """
        return self.preferences

    def generate_preference_profiles(self, bounds):
        """
        Generate preference profiles.
        """
        for criterion in CriterionName:
            # generate 4 thresholds to distinguish between VERY_BAD, BAD, etc.
            min_value, max_value = bounds[criterion.name]
            random_numbers = [
                random.randint(min_value, max_value) for _ in range(len(bounds))
            ]
            self.profile_thresholds[criterion.name] = sorted(random_numbers)

    def generate_preferences(self, criterion_value_list):
        """
        Generate the preference table.
        """
        self.preferences = Preferences()
        # set the name of criterion we use by order of importance
        ordered_crit_names = [crit.name for crit in CriterionName]
        # Shuffle it so that all the agents have different preferences
        random.shuffle(ordered_crit_names)
        self.preferences.set_criterion_name_list(ordered_crit_names)
        # add values (***) for each of the criterion and for each item
        for crit_value_pair in criterion_value_list:
            # object CriterionValue where value is a numerical score
            # convert the value from numerical to stars (***)
            item = crit_value_pair.get_item()
            crit_name = crit_value_pair.get_criterion_name()
            crit_value = crit_value_pair.get_value()
            thresholds = self.profile_thresholds[crit_name]
            index = 0
            for thresh in thresholds:
                if crit_value > thresh:
                    index += 1
            star_value = Value(index)
            self.preferences.add_criterion_value(
                CriterionValue(item, crit_name, star_value)
            )

    def support_proposal(self, item):
        """
        Used when the agent receives "ASK_WHY" after having proposed an item
        :param item: str - name of the item which was proposed
        :return: string - the strongest supportive argument
        """

        argument = Argument(boolean_decision=True, item=item)
        premisses_pro_item = argument.list_supporting_proposal(item, self.preferences)
        best_premiss = premisses_pro_item[0]
        best_premiss_crit_name = best_premiss.get_criterion_name()
        for prem in premisses_pro_item:
            crit_name = prem.get_criterion_name()
            prefered_criterion = self.preferences.is_preferred_criterion(
                best_premiss_crit_name, crit_name
            )
            if not prefered_criterion:
                best_premiss = prem
                best_premiss_crit_name = crit_name
        argument.add_premiss_couple_values(
            criterion_name=best_premiss.get_criterion_name(),
            value=best_premiss.get_value(),
        )
        return argument.__str__()

    def parse_argument(self, argument_str: str):
        """Recover an argument object from an argument string."""
        conclusion_str, premisses_str = argument_str.split("<=")
        boolean_decision = True
        if "NOT" in conclusion_str:
            boolean_decision = False
        item_argument = None
        for item in self.list_items:
            if item.get_name() == conclusion_str.split(" ")[1]:
                item_argument = item
        argument = Argument(boolean_decision=boolean_decision, item=item_argument)
        for prem_str in premisses_str.split(", "):
            if "=" in prem_str:
                crit_str, value_str = prem_str.split("=")
                argument.add_premiss_couple_values(
                    CriterionName[crit_str], Value[value_str]
                )
            elif ">" in prem_str:
                best_str, worst_str = prem_str.split(">")
                argument.add_premiss_comparison(
                    CriterionName[best_str], CriterionName[worst_str]
                )
        return argument

    def attack_argument(self, argument: Argument):
        """Build a list of counter-arguments"""
        counter_arguments = []
        # Find arguments of the form:
        # Argument(NOT Item <= premisses)
        if argument.couple_values_list:
            best_reason = argument.couple_values_list[0]
            best_reason_crit_name = best_reason.get_criterion_name()
            best_reason_crit_value = best_reason.get_criterion_value()
            counter_premisses = argument.list_attacking_proposal(
                argument.item, self.preferences
            )
            for prem in counter_premisses:
                crit_name = prem.get_criterion_name()
                crit_value = prem.get_criterion_value()
                if (
                    crit_name != best_reason_crit_name
                    and not self.preferences.is_preferred_criterion(
                        best_reason_crit_name, crit_name
                    )
                ):
                    counter_arg1 = Argument(boolean_decision=False, item=argument.item)
                    counter_arg1.add_premiss_comparison(
                        crit_name, best_reason_crit_name
                    )
                    counter_arg1.add_premiss_couple_values(crit_name, crit_value)
                    counter_arguments.append(counter_arg1)

                    counter_arg2 = Argument(boolean_decision=False, item=argument.item)
                    counter_arg2.add_premiss_comparison(
                        crit_name, best_reason_crit_name
                    )
                    counter_arguments.append(counter_arg2)

                elif crit_name == best_reason_crit_name:
                    counter_arg = Argument(boolean_decision=False, item=argument.item)
                    counter_arg.add_premiss_couple_values(crit_name, crit_value)
                    counter_arguments.append(counter_arg)

            # Find an argument of the form
            # Arg(Item <= same criteria = Better Value)
            for criterion_value in self.preferences.get_criterion_value_list():
                crit_value_name = criterion_value.get_criterion_name()
                crit_value_item = criterion_value.get_item()
                crit_value_value = criterion_value.get_value()
                if (
                    crit_value_item.get_name() == argument.item.get_name()
                    and crit_value_name == best_reason_crit_name
                    and crit_value_value > best_reason_crit_value
                ):
                    counter_arg = Argument(boolean_decision=True, item=argument.item)
                    counter_arg.add_premiss_couple_values(
                        best_reason_crit_name, crit_value_value
                    )
                    counter_arguments.append(counter_arg)
        return counter_arguments
