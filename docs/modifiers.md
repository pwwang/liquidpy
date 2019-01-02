`liquidpy` has 2 (actually 3) unique modifiers: `*`, `&`( and `@`). 
	- `@` modifier is used to tell the modifier is coming from original `liquid`. 
	- `*` modifier is used to expand the arguments in previous expression.
	- `&` modifier is used to chain the values from previous expression.  

!!! danger
	Expansion (`*`) modifier has to be placed before other modifiers. That is to say: `*&@filter` will be legal, while `&*@filter` is not.

In this section, we will be talking about the expansion and chaining modifiers.

# Expansion modifier: `*`

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
{# with expansion, they can be passed as separate arguments to next filter #}
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
	Or `{{ 1 | :(a,) }} => (1,)`

!!! attention
	For `getitem` and `attribute` filters, expansion modifier will break down the tuple, leaving only the first element. For example:  
	```liquid
	{{ ',', '.' | *.join: ['a', 'b']}}
	{# output: a,b #}
	```

# Chaining modifer: `&`

This modifier brings the values from previous expression. Let's say we want to increment a value if it is an integer, otherwise leave it alone:
```python
Liquid("{{x | @plus: 1}}").render(x = None)
# TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
```
Instead, we could do:
```python
tpl = '{{x | &isinstance: int | *:[a, b+1][int(b)] }}'
Liquid(tpl).render(x = None) # None
Liquid(tpl).render(x = 1) # 2
# the last expression is expanded to:
# (lambda a, b: [a, b+1][int(b)])(
#	x, isinstance(x, int)
# )
# Without & before instance, the argument for lambda is only isinstance(x, int) 
```

__Both modifiers can be used on the same filter__:  

```liquid
{{ 'a,b,c,d', ',' | *&@replace: '|' | :'/'.join(a) }}
{# output: 'a,b,c,d/,/a|b|c|d' #}
```
