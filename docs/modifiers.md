`liquidpy` has 6 unique modifiers: `*`, `@`, `?`, `!`, `=`, `?!` and `?=`.
	- `*` unpacking modifier is used to unpack the tuple values in previous expression.
	- `@` liquid modifier is used to tell that the filter is a `liquid` filter.
	- `?` ternary modifier to mark that this filter is the condition of a ternary operation.
	- `!` ternary modifier to mark that this filter an action when previous condition is True (marked by `?`).
	- `=` ternary modifier to mark that this filter an action when previous condition is False (marked by `?`).
	- `?!` combined ternary modifier to modify the value when it is False-equivalent(, otherwise keep it unchanged).
	- `?=` combined ternary modifier to modify the value when it is True-equivalent(, otherwise keep it unchanged).

In this section, we will be talking about the unpacking modifier.

See [filters](https://liquidpy.readthedocs.io/en/latest/filters/) for liquid modifiers, and [ternary filters](https://liquidpy.readthedocs.io/en/latest/filters/#ternary-filters) for ternary-related modifiers.

# Unpacking modifier: `*`

This modifier is used to flatten to values or expression in the previous expression (before the pipe `|`), so that they can be used as arguments of the filter, instead of a `tuple`.

<div markdown="1" class="two-column">

Input:
```liquid
{# without expansion, it will be a tuple #}
{{"a,b,c,d", "," | repr}}
```

</div>
<div markdown="1" class="two-column">

Output:
```
('a,b,c,d', ',')
```

</div>

---

<div markdown="1" class="two-column">

```liquid
{# with expansion, they can be passed
   as separate arguments to next filter #}
{{"a,b,c,d", "," | *@replace: "|"}}
```

</div>
<div markdown="1" class="two-column">

```
a|b|c|d
```

</div>

---

!!! note
	When there is only one value or expression, it will be always the value itself instead of a tuple. In this case, expansion modifier doesn't work.

	If you want to convert a single value or expression into a tuple, you can add an extra comma next to the value or expression:
	`{{ 1, | repr}} => (1,)`
	Or `{{ (1, ) | repr }} => (1,)`

!!! attention
	For `getitem` and `attribute` filters, unpacking modifier is not allowed.
