"""Grammar utilities for lark grammar.

Here we opens opptunities to operate the grammar, including
add, remove and update
"""
from pathlib import Path
from copy import deepcopy
from diot import OrderedDiot

class Grammar:
    """Manipulate lark grammar

    Args:
        grammar: The grammar. Could be a grammar string or
            a path to grammar file.

    Attributes:
        grammar: The loaded grammar
    """

    def __init__(self, grammar):
        # type: (Union[str, Path]) -> None
        self.grammar = Grammar._load(grammar)

    @staticmethod
    def _load(grammar):
        # type: (Union[str, Path]) -> OrderedDiot
        """Load the base grammar in a very simple way.

        Only name and its following strings
        """
        try:
            if Path(grammar).is_file():
                grammar_lines = open(grammar)
            else:
                raise OSError
        except OSError: # filename too long
            grammar_lines = grammar.splitlines()

        ret = OrderedDiot()
        name = None
        for line in grammar_lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            if line[0] == '|':
                ret[name].assignment.append(line[1:].strip())
            elif line[0] == '%':
                keyword, content = line.split(maxsplit=1)
                content = ' '.join(content.strip().split())
                ret.setdefault(keyword, {'modifier': None, 'assignment': []})
                ret[keyword].assignment.append(content)
            else:
                modifier = None
                if line[0] in ('!', '?'):
                    modifier = line[0]
                    currname, currassign = line[1:].split(':', 1)
                else:
                    currname, currassign = line.split(':', 1)

                currname = currname.strip()
                currassign = currassign.strip()
                ret[currname] = {
                    'modifier': modifier,
                    'assignment': [currassign] if currassign else []
                }
                name = currname

        try:
            grammar_lines.close()
        except AttributeError:
            pass

        return ret

    def copy(self):
        # type: () -> Grammar
        """Copy the grammar object"""
        ret = Grammar('')
        ret.grammar = deepcopy(self.grammar)
        return ret

    def update(self, other):
        # type: (Union[str, Path]) -> None
        """Merge another grammar

        Rule:
        - Existing rules will be extended in the way of
            rule: subrule -> rule: subrule | subrule2
        - Non-existing rules/terminals will be added
        - Unimported statement will be added

        Args:
            other: The other grammar
        """
        other_grammar = (other if isinstance(other, Grammar)
                         else self._load(other))
        for name, content in other_grammar.items():
            if (name[0] == '%' and
                    name in self.grammar and
                    content.assignment[0] in self.grammar[name].assignment[0]):
                continue

            if name in self.grammar:
                assert (
                    not content.modifier or
                    content.modifier == self.grammar[name].modifier
                ), ("Grammar rule with inconsistent modifiers: "
                    f"{name}({self.grammar[name].modifier}, "
                    f"{content.modifier})")

                self.grammar[name].assignment.extend(content.assignment)
            else:
                self.grammar[name] = content


    def __str__(self):
        # type: () -> str
        """Dump the grammar for parser"""
        dumped = []
        dumped_append = dumped.append
        for name, content in self.grammar.items():
            if name[0] == '%':
                for assign in content.assignment:
                    dumped_append(f"{name} {assign}")
            else:
                dumped_append(f"{content.modifier or ''}{name}: "
                              f"{content.assignment[0]}")
                for assign in content.assignment[1:]:
                    dumped_append(f"    | {assign}")
                dumped_append("")
        return '\n'.join(dumped) + '\n'


    def replace(self, rule_or_terminal, replacement):
        # type: (str, str) -> None
        """Replace a rule or a terminal with a replacement

        Args:
            rule_or_terminal: The rule or terminal name
            replacement: The replacement string for the rule or terminal
        """
        if rule_or_terminal not in self.grammar:
            self.add(rule_or_terminal, replacement)

        self.grammar[rule_or_terminal].assignment = [replacement]

    def add_to(self, rule, sub_rule):
        # type: (str, str)
        """Add a sub-rule to a rule

        The rule must be all alternatives (concatenated with "|") or
        an empty rule

        Args:
            rule: The rule name
            sub_rule: The sub-rule
        """
        self.grammar[rule].assignment.append(sub_rule)

    def add(self, rule_or_terminal, assignment, modifier=None):
        # type: (str, str, Optional[str]) -> None
        """Add a new rule or terminal

        Args:
            rule_or_terminaL: The rule or terminal name
            assignment: The assignment for the rule or terminal
            modifier: The modifier for the rule or terminal
        """
        self.grammar[rule_or_terminal] = {
            'modifier': modifier,
            'assignment': [assignment]
        }
