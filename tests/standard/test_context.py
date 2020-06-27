"""Tests grabbed from:
https://github.com/Shopify/liquid/blob/master/test/unit/context_unit_test.rb
"""
import pytest
from liquid.common.tagfrag import (
    TagFragVar, TagFragGetAttr, TagFragOutput, TagFragFilter,
    TagFragGetItem, TagFragConst, TagFragRange
)
from liquid import register_filter
from liquid.config import LIQUID_FILTERS_ENVNAME
from liquid.filtermgr import LIQUID_FILTERS



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
    assert TagFragVar(varname).render(context, {}) == value

def test_variables_not_existing():
    with pytest.raises(KeyError):
        TagFragVar('non_exist').render({}, {})

def test_length_query():
    lenq = TagFragGetAttr(TagFragVar('a'), 'size')

    assert lenq.render({'a': [1,2,3,4]}, {}) == 4
    assert lenq.render({'a': {1:1, 2:2, 3:3, 4:4}}, {}) == 4
    a = lambda: None
    a.size = 1000
    assert lenq.render({'a': a}, {}) == 1000

def test_add_filter():
    @register_filter
    def hi(output):
        return output + ' hi!'

    out = TagFragOutput(
        TagFragVar('hi'),
        [(TagFragFilter('hi'), ())]
    )
    assert out.render({LIQUID_FILTERS_ENVNAME: LIQUID_FILTERS,
                       'hi': 'hi?'},
                      {LIQUID_FILTERS_ENVNAME: LIQUID_FILTERS,
                       'hi': 'hi?'}) == 'hi? hi!'

def test_hierachical_data():
    context = {'a': {'name': 'tobi'}}
    TagFragGetAttr(TagFragVar('a'), 'name').render(context, {}) == 'tobi'
    TagFragGetItem(TagFragVar('a'), TagFragConst('name')).render(
        context, {}
    ) == 'tobi'


@pytest.mark.parametrize('val', [
    True, False, 100, 100.00, 'Hello!', "Hello!"
])
def test_constants(val):
    assert TagFragConst(val).render({}, {}) == val


def test_array_notation():
    context = {}
    context['test'] = [1, 2, 3, 4, 5]

    assert TagFragGetItem(TagFragVar('test'),
                          TagFragConst(0)).render(context, {}) == 1
    assert TagFragGetItem(TagFragVar('test'),
                          TagFragConst(1)).render(context, {}) == 2
    assert TagFragGetItem(TagFragVar('test'),
                          TagFragConst(2)).render(context, {}) == 3
    assert TagFragGetItem(TagFragVar('test'),
                          TagFragConst(3)).render(context, {}) == 4
    assert TagFragGetItem(TagFragVar('test'),
                          TagFragConst(4)).render(context, {}) == 5


def test_recoursive_array_notation():
    context = {}
    context['test'] = {}
    context['test']['test']= [1, 2, 3, 4, 5]

    assert TagFragGetItem(
        TagFragGetAttr(TagFragVar('test'), 'test'),
        TagFragConst(0)
    ).render(context, {}) == 1

    context['test'] = [{ 'test' : 'worked' }]
    assert TagFragGetAttr(
        TagFragGetItem(TagFragVar('test'), TagFragConst(0)),
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
    assert TagFragGetItem(
        TagFragGetAttr(TagFragVar('colors'), 'Blue'),
        TagFragConst(0)
    ).render(context, {}) == '003366'

    assert TagFragGetItem(
        TagFragGetAttr(TagFragVar('colors'), 'Red'),
        TagFragConst(3)
    ).render(context, {}) == 'FF9999'


def test_try_first():
    context = {}
    context['test'] = [1, 2, 3, 4, 5]

    assert TagFragGetAttr(TagFragVar('test'), 'first').render(context, {}) == 1
    assert TagFragGetAttr(TagFragVar('test'), 'last').render(context, {}) == 5

    context['test'] = { 'test' : [1, 2, 3, 4, 5] }

    assert TagFragGetAttr(
        TagFragGetAttr(TagFragVar('test'), 'test'),
        'first'
    ).render(context, {}) == 1
    assert TagFragGetAttr((
        TagFragGetAttr(TagFragVar('test'), 'test'),
        'last'
    )).render(context, {}) == 5

    context['test'] = [1]
    assert TagFragGetAttr(TagFragVar('test'), 'first').render(context, {}) == 1
    assert TagFragGetAttr(TagFragVar('test'), 'last').render(context, {}) == 1

def test_access_hashes_with_hash_notation():
    context = {}
    context['products'] = { 'count' : 5, 'tags' : ['deepsnow', 'freestyle'] }
    context['product']  = { 'variants' : [{ 'title' : 'draft151cm' },
                                          { 'title' : 'element151cm' }] }

    assert TagFragGetItem(
        TagFragVar('products'),
        TagFragConst('count')
    ).render(context, {}) == 5

    assert TagFragGetItem( TagFragGetItem(
        TagFragVar('products'),
        TagFragConst('tags')
    ), TagFragConst(0)).render(context, {}) == 'deepsnow'

    assert TagFragGetAttr( TagFragGetItem(
        TagFragVar('products'),
        TagFragConst('tags')
    ), 'first').render(context, {}) == 'deepsnow'

    assert TagFragGetItem(
        TagFragGetItem( TagFragGetItem(
                TagFragVar('product'),
                TagFragConst('variants')
            ),
            TagFragConst(0)
        ),
        TagFragConst('title')
    ) .render(context, {}) == 'draft151cm'

    assert TagFragGetItem(
        TagFragGetItem( TagFragGetItem(
                TagFragVar('product'),
                TagFragConst('variants')
            ),
            TagFragConst(1)
        ),
        TagFragConst('title')
    ) .render(context, {}) == 'element151cm'

    assert TagFragGetItem(
        TagFragGetAttr( TagFragGetItem(
                TagFragVar('product'),
                TagFragConst('variants')
            ),
            'first'
        ),
        TagFragConst('title')
    ) .render(context, {}) == 'draft151cm'

    assert TagFragGetItem(
        TagFragGetAttr( TagFragGetItem(
                TagFragVar('product'),
                TagFragConst('variants')
            ),
            'last'
        ),
        TagFragConst('title')
    ) .render(context, {}) == 'element151cm'

def test_access_variable_with_hash_notation():
    context = {'a': {}}
    context['a']['foo'] = 'baz'
    context['bar'] = 'foo'

    assert TagFragGetItem((
        TagFragVar('a'),
        TagFragConst('foo')
    )).render(context, {}) == 'baz'

    assert TagFragGetItem((
        TagFragVar('a'),
        TagFragVar('bar')
    )).render(context, {}) == 'baz'


def test_access_hashes_with_hash_access_variables():
    context = {}
    context['var']      = 'tags'
    context['nested']   = { 'var' : 'tags' }
    context['products'] = { 'count' : 5, 'tags' : ['deepsnow', 'freestyle'] }

    assert TagFragGetAttr(
        TagFragGetItem(
            TagFragVar('products'),
            TagFragVar('var')
        ),
        'first'
    ).render(context, {}) == 'deepsnow'

    assert TagFragGetAttr(
        TagFragGetItem(
            TagFragVar('products'),
            TagFragGetAttr(
                TagFragVar('nested'),
                'var'
            )
        ),
        'last'
    ) .render(context, {}) == 'freestyle'

def test_hash_notation_only_for_hash_access():
    context = {}
    context['array'] = [1, 2, 3, 4, 5]
    context['hash']  = { 'first' : 'Hello' }

    assert TagFragGetAttr(
        TagFragVar('array'), 'first'
    ).render(context, {}) == 1

    with pytest.raises(TypeError):
        TagFragGetItem(TagFragVar('array'),
                       TagFragConst('first')).render(context, {})

    assert TagFragGetItem(
        TagFragVar('hash'),
        TagFragConst('first')
    ).render(context, {}) == 'Hello'

def test_first_can_appear_in_middle_of_callchain():
    context = {}
    context['product'] = { 'variants' : [{ 'title' : 'draft151cm' },
                                         { 'title' : 'element151cm' }] }

    assert TagFragGetAttr(
        TagFragGetItem(
            TagFragGetAttr(TagFragVar('product'), 'variants'),
            TagFragConst(0)
        ),
        'title'
    ) .render(context, {}) == 'draft151cm'

    assert TagFragGetAttr(
        TagFragGetItem(
            TagFragGetAttr(TagFragVar('product'), 'variants'),
            TagFragConst(1)
        ),
        'title'
    ) .render(context, {}) == 'element151cm'

    assert TagFragGetAttr(
        TagFragGetAttr(
            TagFragGetAttr(TagFragVar('product'), 'variants'),
            'first'
        ),
        'title'
    ) .render(context, {}) == 'draft151cm'

    assert TagFragGetAttr(
        TagFragGetAttr(
            TagFragGetAttr(TagFragVar('product'), 'variants'),
            'last'
        ),
        'title'
    ) .render(context, {}) == 'element151cm'

def test_ranges():
    context = {}
    context["test"] = '5'

    assert TagFragRange(TagFragConst(1),
                        TagFragConst(5)).render(context, {}) == [1,2,3,4,5]
    assert TagFragRange(TagFragConst(1),
                        TagFragVar('test')).render(context, {}) == [1,2,3,4,5]
    assert TagFragRange(TagFragVar('test'),
                        TagFragVar('test')).render(context, {}) == [5]


def test_new_isolated_subcontext_inherits_filters():

    from liquid import register_filter

    @register_filter
    def my_filter(*args):
        return 'my filter result'

    out = TagFragOutput(
        TagFragConst(123),
        [(TagFragFilter('my_filter'), ())]
    )
    assert out.render({LIQUID_FILTERS_ENVNAME: LIQUID_FILTERS,
                       'hi': 'hi?'},
                      {LIQUID_FILTERS_ENVNAME: LIQUID_FILTERS,
                       'hi': 'hi?'}) == 'my filter result'
