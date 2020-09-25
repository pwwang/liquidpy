"""Tests grabbed from:
https://github.com/Shopify/liquid/blob/master/test/unit/context_unit_test.rb
"""
import pytest
from lark import Token
from liquid.tags.transformer import *
from liquid import *
from liquid.config import LIQUID_FILTERS_ENVNAME

@pytest.mark.parametrize('context,varname,value', [
    (dict(string='string'), 'string', 'string'),
    (dict(num=5), 'num', 5),
    # not time obj in python, we do object instead
    (dict(time={'date': '2006-06-06 12:00:00'}), 'time',
     {'date': '2006-06-06 12:00:00'}),
    (dict(date={'date': '2006-06-06'}), 'date',
     {'date': '2006-06-06'}),
    (dict(bool=False), 'bool', False),
    (dict(bool=True), 'bool', True),
    (dict(nil=None), 'nil', None),
    # test_hyphenated_variable
    ({'oh-my': 'godz'}, 'oh-my', 'godz'),
])
def test_variables(context, varname, value):
    assert TagSegmentVar(Token(value=varname, type_='str')).render(
        context, {}
    ) == value

def test_variables_not_existing():
    with pytest.raises(LiquidNameError):
        TagSegmentVar(Token(value='non_exist', type_='str')).render({}, {})

def test_length_query():
    lenq = TagSegmentGetAttr(TagSegmentVar('a'), 'size')

    assert lenq.render({'a': [1,2,3,4]}, {}) == 4
    assert lenq.render({'a': {1:1, 2:2, 3:3, 4:4}}, {}) == 4
    a = lambda: None
    a.size = 1000
    assert lenq.render({'a': a}, {}) == 1000

def test_add_filter():
    @filter_manager.register
    def hi(output):
        return output + ' hi!'

    out = TagSegmentOutput(
        TagSegmentVar('hi'),
        TagSegmentFilter('hi', None),
    )
    assert out.render(
        {'hi': 'hi?', LIQUID_FILTERS_ENVNAME: filter_manager.filters},
        {'hi': 'hi?', LIQUID_FILTERS_ENVNAME: filter_manager.filters}
    ) == 'hi? hi!'

def test_hierachical_data():
    context = {'a': {'name': 'tobi'}}
    TagSegmentGetAttr(TagSegmentVar('a'), 'name').render(context, {}) == 'tobi'
    TagSegmentGetItem(TagSegmentVar('a'), 'name').render(
        context, {}
    ) == 'tobi'


def test_array_notation():
    context = {}
    context['test'] = [1, 2, 3, 4, 5]

    assert TagSegmentGetItem(TagSegmentVar('test'),
                          0).render(context, {}) == 1
    assert TagSegmentGetItem(TagSegmentVar('test'),
                          1).render(context, {}) == 2
    assert TagSegmentGetItem(TagSegmentVar('test'),
                          2).render(context, {}) == 3
    assert TagSegmentGetItem(TagSegmentVar('test'),
                          3).render(context, {}) == 4
    assert TagSegmentGetItem(TagSegmentVar('test'),
                          4).render(context, {}) == 5


def test_recoursive_array_notation():
    context = {}
    context['test'] = {}
    context['test']['test']= [1, 2, 3, 4, 5]

    assert TagSegmentGetItem(
        TagSegmentGetAttr(TagSegmentVar('test'), 'test'),
        0
    ).render(context, {}) == 1

    context['test'] = [{ 'test' : 'worked' }]
    assert TagSegmentGetAttr(
        TagSegmentGetItem(TagSegmentVar('test'), 0),
        'test'
    ).render(context, {}) == 'worked'


def test_hash_to_array_transition():
    context = {}
    context['colors'] = {
      'Blue' : ['003366', '336699', '6699CC', '99CCFF'],
      'Green' : ['003300', '336633', '669966', '99CC99'],
      'Yellow' : ['CC9900', 'FFCC00', 'FFFF99', 'FFFFCC'],
      'Red' : ['660000', '993333', 'CC6666', 'FF9999'],
    }
    assert TagSegmentGetItem(
        TagSegmentGetAttr(TagSegmentVar('colors'), 'Blue'),
        0
    ).render(context, {}) == '003366'

    assert TagSegmentGetItem(
        TagSegmentGetAttr(TagSegmentVar('colors'), 'Red'),
        3
    ).render(context, {}) == 'FF9999'


def test_try_first():
    context = {}
    context['test'] = [1, 2, 3, 4, 5]

    assert TagSegmentGetAttr(TagSegmentVar('test'), 'first').render(
        context, {}
    ) == 1
    assert TagSegmentGetAttr(TagSegmentVar('test'), 'last').render(
        context, {}
    ) == 5

    context['test'] = { 'test' : [1, 2, 3, 4, 5] }

    assert TagSegmentGetAttr(
        TagSegmentGetAttr(TagSegmentVar('test'), 'test'),
        'first'
    ).render(context, {}) == 1
    assert TagSegmentGetAttr(
        TagSegmentGetAttr(TagSegmentVar('test'), 'test'),
        'last'
    ).render(context, {}) == 5

    context['test'] = [1]
    assert TagSegmentGetAttr(TagSegmentVar('test'), 'first').render(context, {}) == 1
    assert TagSegmentGetAttr(TagSegmentVar('test'), 'last').render(context, {}) == 1

def test_access_hashes_with_hash_notation():
    context = {}
    context['products'] = { 'count' : 5, 'tags' : ['deepsnow', 'freestyle'] }
    context['product']  = { 'variants' : [{ 'title' : 'draft151cm' },
                                          { 'title' : 'element151cm' }] }

    assert TagSegmentGetItem(
        TagSegmentVar('products'),
        'count'
    ).render(context, {}) == 5

    assert TagSegmentGetItem( TagSegmentGetItem(
        TagSegmentVar('products'),
        'tags'
    ), 0).render(context, {}) == 'deepsnow'

    assert TagSegmentGetAttr( TagSegmentGetItem(
        TagSegmentVar('products'),
        'tags'
    ), 'first').render(context, {}) == 'deepsnow'

    assert TagSegmentGetItem(
        TagSegmentGetItem( TagSegmentGetItem(
                TagSegmentVar('product'),
                'variants'
            ),
            0
        ),
        'title'
    ) .render(context, {}) == 'draft151cm'

    assert TagSegmentGetItem(
        TagSegmentGetItem( TagSegmentGetItem(
                TagSegmentVar('product'),
                'variants'
            ),
            1
        ),
        'title'
    ) .render(context, {}) == 'element151cm'

    assert TagSegmentGetItem(
        TagSegmentGetAttr( TagSegmentGetItem(
                TagSegmentVar('product'),
                'variants'
            ),
            'first'
        ),
        'title'
    ) .render(context, {}) == 'draft151cm'

    assert TagSegmentGetItem(
        TagSegmentGetAttr( TagSegmentGetItem(
                TagSegmentVar('product'),
                'variants'
            ),
            'last'
        ),
        'title'
    ) .render(context, {}) == 'element151cm'

def test_access_variable_with_hash_notation():
    context = {'a': {}}
    context['a']['foo'] = 'baz'
    context['bar'] = 'foo'

    assert TagSegmentGetItem(
        TagSegmentVar('a'),
        'foo'
    ).render(context, {}) == 'baz'

    assert TagSegmentGetItem(
        TagSegmentVar('a'),
        TagSegmentVar('bar')
    ).render(context, {}) == 'baz'


def test_access_hashes_with_hash_access_variables():
    context = {}
    context['var']      = 'tags'
    context['nested']   = { 'var' : 'tags' }
    context['products'] = { 'count' : 5, 'tags' : ['deepsnow', 'freestyle'] }

    assert TagSegmentGetAttr(
        TagSegmentGetItem(
            TagSegmentVar('products'),
            TagSegmentVar('var')
        ),
        'first'
    ).render(context, {}) == 'deepsnow'

    assert TagSegmentGetAttr(
        TagSegmentGetItem(
            TagSegmentVar('products'),
            TagSegmentGetAttr(
                TagSegmentVar('nested'),
                'var'
            )
        ),
        'last'
    ) .render(context, {}) == 'freestyle'

def test_hash_notation_only_for_hash_access():
    context = {}
    context['array'] = [1, 2, 3, 4, 5]
    context['hash']  = { 'first' : 'Hello' }

    assert TagSegmentGetAttr(
        TagSegmentVar('array'), 'first'
    ).render(context, {}) == 1

    with pytest.raises(TypeError):
        TagSegmentGetItem(TagSegmentVar('array'),
                       'first').render(context, {})

    assert TagSegmentGetItem(
        TagSegmentVar('hash'),
        'first'
    ).render(context, {}) == 'Hello'

def test_first_can_appear_in_middle_of_callchain():
    context = {}
    context['product'] = { 'variants' : [{ 'title' : 'draft151cm' },
                                         { 'title' : 'element151cm' }] }

    assert TagSegmentGetAttr(
        TagSegmentGetItem(
            TagSegmentGetAttr(TagSegmentVar('product'), 'variants'),
            0
        ),
        'title'
    ) .render(context, {}) == 'draft151cm'

    assert TagSegmentGetAttr(
        TagSegmentGetItem(
            TagSegmentGetAttr(TagSegmentVar('product'), 'variants'),
            1
        ),
        'title'
    ) .render(context, {}) == 'element151cm'

    assert TagSegmentGetAttr(
        TagSegmentGetAttr(
            TagSegmentGetAttr(TagSegmentVar('product'), 'variants'),
            'first'
        ),
        'title'
    ) .render(context, {}) == 'draft151cm'

    assert TagSegmentGetAttr(
        TagSegmentGetAttr(
            TagSegmentGetAttr(TagSegmentVar('product'), 'variants'),
            'last'
        ),
        'title'
    ) .render(context, {}) == 'element151cm'

def test_ranges():
    context = {}
    context["test"] = '5'

    assert TagSegmentRange(
        1,
        5).render(context, {}
    ) == [1,2,3,4,5]
    assert TagSegmentRange(
        1,
        TagSegmentVar('test')).render(context, {}
    ) == [1,2,3,4,5]
    assert TagSegmentRange(
        TagSegmentVar('test'),
        TagSegmentVar('test')).render(context, {}
    ) == [5]


def test_new_isolated_subcontext_inherits_filters():

    @filter_manager.register
    def my_filter(*args):
        return 'my filter result'

    out = TagSegmentOutput(
        123,
        TagSegmentFilter('my_filter', None)
    )
    assert out.render(
        {'hi': 'hi?', LIQUID_FILTERS_ENVNAME: filter_manager.filters},
        {'hi': 'hi?', LIQUID_FILTERS_ENVNAME: filter_manager.filters}
    ) == 'my filter result'
