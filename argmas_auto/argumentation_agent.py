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
from argmas_auto.communication.preferences.Preferences import Preferences
from argmas_auto.communication.preferences.Value import Value
from argmas_auto.communication.preferences.CriterionName import CriterionName
from argmas_auto.communication.preferences.CriterionValue import CriterionValue


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
        if self.name == "You":
            # You read the message you received
            messages = self.get_new_messages()
            if messages:
                print(f"{self.name} received: {messages[0]}")
            if not messages and not self.conversation_started[self.dest_name]:
                # Starting the conversation with a PROPOSE
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
                # You proposed an engine and received an ASK_WHY: argue for your proposal
                best_argument = self.support_proposal(self.preferred_item)
                if best_argument:
                    mess = Message(
                        self.name,
                        self.dest_name,
                        MessagePerformative.ARGUE,
                        best_argument,
                    )
                    self.send_message(mess)
                else:
                    self.remove_item_from_choices(item=self.preferred_item)
                    self.preferred_item = self.preferences.most_preferred(
                        self.list_items
                    )
                    mess = Message(
                        self.name,
                        self.dest_name,
                        MessagePerformative.PROPOSE,
                        self.preferred_item,
                    )
                    self.send_message(mess)

            elif (
                messages
                and messages[0].get_performative() == MessagePerformative.ACCEPT
            ):
                # Luke accepted the item, You terminate the conversation
                mess = Message(
                    self.name,
                    self.dest_name,
                    MessagePerformative.COMMIT,
                    messages[0].get_content(),
                )
                self.send_message(mess)
                # remove the accepted item from the list of items
                self.remove_item_from_choices(self.preferred_item)

            elif (
                messages and messages[0].get_performative() == MessagePerformative.ARGUE
            ):
                pro_argument = self.parse_argument(
                    argument_str=messages[0].get_content()
                )
                con_arguments = self.attack_argument(pro_argument)
                if con_arguments:
                    # Choose one counter-argument at random
                    chosen_con_arg = random.choice(con_arguments)
                    mess = Message(
                        self.name,
                        self.dest_name,
                        MessagePerformative.ARGUE,
                        content=str(chosen_con_arg),
                    )
                    self.send_message(mess)
                else:
                    mess = Message(
                        self.name,
                        self.dest_name,
                        MessagePerformative.ACCEPT,
                        pro_argument.item,
                    )
                    self.send_message(mess)
            elif (
                messages
                and messages[0].get_performative() == MessagePerformative.PROPOSE
            ):
                is_among_top_10 = self.preferences.is_item_among_top_10_percent(
                    item=messages[0].get_content(), item_list=self.list_items
                )
                if is_among_top_10:
                    print(f"The engine is among {self.name}'s top 10%.")
                    # item proposed in the top 10% of Luke
                    self.preferred_item = self.preferences.most_preferred(
                        self.list_items
                    )
                    if (
                        self.preferred_item.get_name()
                        != messages[0].get_content().get_name()
                    ):
                        print("Proposing even better.")
                        mess = Message(
                            self.name,
                            self.dest_name,
                            MessagePerformative.PROPOSE,
                            content=self.preferred_item,
                        )
                        self.send_message(mess)
                    else:
                        print("Accepting the proposal.")
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

        if self.name == "Luke":
            messages = self.get_new_messages()
            if messages:
                print(f"{self.name} received: {messages[0]}")
            if (
                messages
                and messages[0].get_performative() == MessagePerformative.PROPOSE
            ):
                is_among_top_10 = self.preferences.is_item_among_top_10_percent(
                    item=messages[0].get_content(), item_list=self.list_items
                )
                if is_among_top_10:
                    print(f"The engine is among {self.name}'s top 10%.")
                    # item proposed in the top 10% of Luke
                    self.preferred_item = self.preferences.most_preferred(
                        self.list_items
                    )
                    if (
                        self.preferred_item.get_name()
                        != messages[0].get_content().get_name()
                    ):
                        print("Proposing even better.")
                        mess = Message(
                            self.name,
                            self.dest_name,
                            MessagePerformative.PROPOSE,
                            content=self.preferred_item,
                        )
                        self.send_message(mess)
                    else:
                        print("Accepting the proposal.")
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
                # Luke knows that You terminates and terminates himself
                mess = Message(
                    self.name,
                    self.dest_name,
                    MessagePerformative.COMMIT,
                    messages[0].get_content(),
                )
                self.send_message(mess)
                self.remove_item_from_choices(messages[0].get_content())

            elif (
                messages and messages[0].get_performative() == MessagePerformative.ARGUE
            ):
                pro_argument = self.parse_argument(
                    argument_str=messages[0].get_content()
                )
                con_arguments = self.attack_argument(pro_argument)
                if con_arguments:
                    # Choose one counter-argument at random
                    chosen_con_arg = random.choice(con_arguments)
                    mess = Message(
                        self.name,
                        self.dest_name,
                        MessagePerformative.ARGUE,
                        content=str(chosen_con_arg),
                    )
                    self.send_message(mess)
                else:
                    mess = Message(
                        self.name,
                        self.dest_name,
                        MessagePerformative.ACCEPT,
                        pro_argument.item,
                    )
                    self.send_message(mess)

            elif (
                messages
                and messages[0].get_performative() == MessagePerformative.ASK_WHY
            ):
                # You proposed an engine and received an ASK_WHY: argue for your proposal
                best_argument = self.support_proposal(self.preferred_item)
                if best_argument:
                    mess = Message(
                        self.name,
                        self.dest_name,
                        MessagePerformative.ARGUE,
                        best_argument,
                    )
                    self.send_message(mess)
                else:
                    self.remove_item_from_choices(item=self.preferred_item)
                    self.preferred_item = self.preferences.most_preferred(
                        self.list_items
                    )
                    mess = Message(
                        self.name,
                        self.dest_name,
                        MessagePerformative.PROPOSE,
                        self.preferred_item,
                    )
                    self.send_message(mess)
            elif (
                messages
                and messages[0].get_performative() == MessagePerformative.ACCEPT
            ):
                # You accepted the item, Luke terminates the conversation
                mess = Message(
                    self.name,
                    self.dest_name,
                    MessagePerformative.COMMIT,
                    messages[0].get_content(),
                )
                self.send_message(mess)

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
            random_numbers = [random.randint(min_value, max_value) for _ in range(4)]
            self.profile_thresholds[criterion] = sorted(random_numbers)

    def generate_preferences(self, criterion_value_list):
        """
        Generate the preference table.
        """
        self.preferences = Preferences()
        # set the name of criterion we use by order of importance
        ordered_crit_names = [crit for crit in CriterionName]
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
        if premisses_pro_item:
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
                value=best_premiss.get_criterion_value(),
            )
            return argument.__str__()
        else:
            return None

    def parse_argument(self, argument_str: str):
        """Recover an argument object from an argument string."""
        conclusion_str, premisses_str = argument_str.split("<=")
        conclusion_str = conclusion_str.replace(" ", "")
        premisses_str = premisses_str.replace(" ", "")
        if "NOT" in conclusion_str:
            boolean_decision = False
            item_str = conclusion_str.split("NOT")[1]
        else:
            boolean_decision = True
            item_str = conclusion_str
        item_argument = None
        for item in self.list_items:
            if item.get_name() == item_str:
                item_argument = item
        argument = Argument(boolean_decision=boolean_decision, item=item_argument)
        for prem_str in premisses_str.split(","):
            prem_str = prem_str.replace(" ", ",")
            if "=" in prem_str:
                crit_str, value_str = prem_str.split("=")
                # Remove white spaces
                crit_str = crit_str.replace(" ", "")
                value_str = value_str.replace(" ", "")
                argument.add_premiss_couple_values(
                    CriterionName[crit_str], Value[value_str]
                )
            elif ">" in prem_str:
                best_str, worst_str = prem_str.split(">")
                best_str = best_str.replace(" ", "")
                worst_str = worst_str.replace(" ", "")
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

    def remove_item_from_choices(self, item: Item):
        """Remove an item from the list of possible items."""
        idx_to_remove = 0
        for idx, possible_item in enumerate(self.list_items):
            if possible_item.get_name() == item.get_name():
                idx_to_remove = idx
        self.list_items.pop(idx_to_remove)
