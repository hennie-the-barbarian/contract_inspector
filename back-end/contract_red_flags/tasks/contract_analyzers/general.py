from .base_classes import ContractInfo
import re

def binding_arbitration_analysis(contract, is_unusual=False):
    label = 'Binding Arbitration'
    link = 'https://en.wikipedia.org/wiki/Arbitration_in_the_United_States#Arbitration_clauses'
    level = ['WARNING', 'yellow']
    description_unusual = "Binding arbitration clauses are non-standard in this type of contract."
    description_usual = "Binding arbitration clauses are standard in this type of contract."
    description_all = (
        " Binding arbitration clauses mean that you are unable to sue the other person in a court "
        "over this agreement. The specifics of how the binding arbitration process works will vary "
        "depending on the specifics of the clause."
    )

    regex = re.compile(r'[bB]inding [aA]rbitration')
    regex_res = regex.search(contract)

    if regex_res:
        description = description_unusual if is_unusual else description_usual
        description += description_all
        return ContractInfo(
            concern_name=label,
            concern_level=level,
            more_info=link,
            description=description
        )
    else:
        return None