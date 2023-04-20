""" 
Implement Arguments.
"""
from argmas_auto.communication.preferences.Value import Value
from argmas_auto.arguments.Comparison import Comparison
from argmas_auto.arguments.CoupleValue import CoupleValue


class Argument:
    """
    Argument class.
    This class implements an argument used during the interaction.
    attr:
    decision:
    item:
    comparison_list:
    couple_values_list:
    """

    def __init__(self, boolean_decision, item):
        """
        Creates a new Argument.
        """
        self.couple_values_list = []
        self.comparison_list = []
        self.boolean_decision = boolean_decision
        self.item = item

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        """
        Adds a premiss comparison in the comparison list.
        By default, criterion_name_1 > criterion_name_2
        """
        self.comparison_list.append(Comparison(criterion_name_1, criterion_name_2))

    def add_premiss_couple_values(self, criterion_name, value):
        """
        Add a premiss couple values in the couple values list.
        """
        self.couple_values_list.append(CoupleValue(criterion_name, value))

    def __str__(self):
        string = ""
        if not self.boolean_decision:
            string += "NOT " + self.item.get_name() + " <= "
        else:
            string += self.item.get_name() + " <= "
        premisses = [comp.__str__() for comp in self.comparison_list] + [
            couple_val.__str__() for couple_val in self.couple_values_list
        ]
        return string + ", ".join(premisses)

    def list_supporting_proposal(self, item, preferences):
        """
        Generate a list of premisses which can be used to support an item
        :param item: Item - name of the item
        :return: list of all premisses PRO an item (sorted by order of importance
        based on agent's preferences)
        """
        # values here are star-values! (***)
        premisses_pro_item = []
        criterions_names = preferences.get_criterion_name_list()
        agent_values = [
            item.get_value(preferences, crit_name) for crit_name in criterions_names
        ]
        agent_valuation = zip(criterions_names, agent_values)
        for name, value in agent_valuation:
            if value > Value.AVERAGE:
                premisses_pro_item.append(CoupleValue(name, value))
        return premisses_pro_item

    def list_attacking_proposal(self, item, preferences):
        """
        Generate a list of premisses which can be used to attack an item
        :param item: Item - name of the item
        :return: list of all premisses CON an item (sorted by order of importance
        based on preferences)
        """
        premisses_against_item = []
        criterions_names = preferences.get_criterion_name_list()
        agent_values = [
            item.get_value(preferences, crit_name) for crit_name in criterions_names
        ]
        agent_valuation = zip(criterions_names, agent_values)
        for name, value in agent_valuation:
            if value < Value.AVERAGE:
                premisses_against_item.append(CoupleValue(name, value))
        return premisses_against_item
