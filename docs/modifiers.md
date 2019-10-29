`liquidpy` has 3 unique modifiers: `*`, `?` and `@`.
	- `@` liquid modifier is used to tell that the filter is a `liquid` filter.
	- `*` unpacking modifier is used to unpack the tuple values in previous expression.
	- `?` ternary modifier is used to mark that this filter is the condition of a ternary operation.

In this section, we will be talking about the unpacking and ternary modifiers.

See [filters](https://liquidpy.readthedocs.io/en/latest/filters/) for liquid modifiers.

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

# ternary modifer: `?`

The ternary modifier marks a filter as a condition of a ternary operation, and initates it.
```liquid
{{ x | ?bool | : "Yes" | : "No" }}
```
It has to be followed by two filters, one calculates the value when the condition is True, the other does when the condition is False.

You can also use the base value as the argument for the True/False filters:

```liquid
{{ x | ?bool | : str(_) +  " is true" | : str(_) + " is false"
```

You may also chain another filter after the ternary:

```liquid
{{ x | ?bool | : str(_), "true" | : str(_), "false" | @join: " is "
```
