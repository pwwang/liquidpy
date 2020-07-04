"""Grammar utilities for lark grammar.

Here we opens opptunities to operate the grammar, including
add, remove, change tags

Now only applies to tags!
"""

from pathlib import Path
from contextlib import suppress
from diot import OrderedDiot

class Grammar:
    """Manipulate lark grammar"""

    def __init__(self, grammar):
        self.grammar = self._load(grammar)

    def _load(self, grammar) -> OrderedDiot:
        """Load the base grammar in a very simple way.

        Only name and its following strings
        """
        try:
            if Path(grammar).is_file():
                grammar_lines = open(grammar)
            else:
                raise OSError()
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
                ret.setdefault(keyword, {'modifier': None,
                                         'assignment': []})
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

        with suppress(AttributeError):
            grammar_lines.close()

        return ret

    def update(self, other):
        """Merge another grammar

        Rule:
        - Existing rules will be extended in the way of
            rule: subrule -> rule: subrule | subrule2
        - Non-existing rules/terminals will be added
        - Unimported statement will be added
        """
        other_grammar = (other if isinstance(other, Grammar)
                         else self._load(other))

        for name, content in other_grammar.items():
            if (name[0] == '%' and
                    name in self.grammar[name] and
                    content in self.grammar[name].assignment):
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
        """Replace a rule or a terminal with a replacement"""
        if rule_or_terminal in self.grammar:
            self.add(rule_or_terminal, replacement)

        self.grammar[rule_or_terminal].assignment = [replacement]

    def add_to(self, rule, sub_rule):
        """Add a sub-rule to a rule

        The rule must be all alternatives (concatenated with "|") or
        an empty rule
        """
        self.grammar[rule].assignment.append(sub_rule)

    def add(self, rule_or_terminal, assignment, modifier=None):
        """Add a new rule or terminal"""
        self.grammar[rule_or_terminal] = {
            'modifier': modifier,
            'assignment': [assignment]
        }

BASE_GRAMMAR = Grammar(Path(__file__).parent / 'grammar.lark')
