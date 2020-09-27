"""Tests grabbed from:
https://github.com/Shopify/liquid/blob/master/test/unit/condition_unit_test.rb
"""
import pytest
from liquid.tags.transformer import *

@pytest.fixture
def render(left, op, right):
    left = render_segment(left, {}, {})
    right = render_segment(right, {}, {})
    return TagSegmentComparison(left, op, right).render({}, {})

@pytest.fixture
def render_func():
    def func(left, op, right):
        left = render_segment(left, {}, {})
        right = render_segment(right, {}, {})
        return TagSegmentComparison(left, op, right).render({}, {})
    return func

@pytest.fixture
def op_compare():
    def func(left, op, right):
        left = render_segment(left, {}, {}) if not isinstance(left, TagSegment) else left
        right = render_segment(right, {}, {}) if not isinstance(right, TagSegment) else right
        return TagSegmentComparison(left, op, right)
    return func

@pytest.fixture
def op_logical():
    def func(left, op, right):
        left = render_segment(left, {}, {}) if not isinstance(left, TagSegment) else left
        right = render_segment(right, {}, {}) if not isinstance(right, TagSegment) else right
        return TagSegmentLogical(left, op, right)
    return func

@pytest.mark.parametrize('left,op,right, result', [
    (1, '==', 2, False),
    (1, '==', 1, True)
])
def test_basic_conditions(left, op, right, result, render):
    assert render == result

@pytest.mark.parametrize('left,op,right', [
    (1, '==', 1),
    (1, '!=', 2),
    (1, '<>', 2),
    (1, '<', 2),
    (2, '>', 1),
    (1, '>=', 1),
    (2, '>=', 1),
    (1, '<=', 2),
    (1, '<=', 1),
    (1, '>', -1),
    (-1, '<', 1),
    (1.0, '>', -1.0),
    (-1.0, '<', 1.0),
])
def test_default_operators_evalute_true(left, op, right, render):
    assert render == True

@pytest.mark.parametrize('left,op,right', [
    (1, '==', 2),
    (1, '!=', 1),
    (1, '<>', 1),
    (1, '<', 0),
    (2, '>', 4),
    (1, '>=', 3),
    (2, '>=', 4),
    (1, '<=', 0),
    (1, '<=', 0),
])
def test_default_operators_evalute_false(left, op, right, render):
    assert render == False

@pytest.mark.parametrize('left,op,right, result', [
    ('bob', 'contains', 'o', True),
    ('bob', 'contains', 'b', True),
    ('bob', 'contains', 'bo', True),
    ('bob', 'contains', 'ob', True),
    ('bob', 'contains', 'bob', True),
    ('bob', 'contains', 'bob2', False),
    ('bob', 'contains', 'a', False),
    ('bob', 'contains', '---', False),
])
def test_contains_works_on_strings(left, op, right, result, render):
    assert render == result

@pytest.mark.parametrize('left,op,right', [
    ('1', '>', 0),
    ('1', '<', 0),
    ('1', '>=', 0),
    ('1', '<=', 0),
    # test_contains_return_false_on_wrong_data_type
    (0, 'contains', 1),
    # test_contains_returns_false_for_nil_operands
    (0, 'contains', "not_assigned"),
])
def test_comparation_of_int_and_str(left, op, right, render_func):
    with pytest.raises(TypeError):
        render_func(left, op, right)

@pytest.mark.parametrize('left,op,right, result', [
    ([1, 2, 3, 4, 5], 'contains', 0, False),
    ([1, 2, 3, 4, 5], 'contains', 1, True),
    ([1, 2, 3, 4, 5], 'contains', 2, True),
    ([1, 2, 3, 4, 5], 'contains', 3, True),
    ([1, 2, 3, 4, 5], 'contains', 4, True),
    ([1, 2, 3, 4, 5], 'contains', 5, True),
    ([1, 2, 3, 4, 5], 'contains', 6, False),
    ([1, 2, 3, 4, 5], 'contains', "1", False),
    # test_contains_returns_false_for_nil_operands
    ('not_assigned', 'contains', '0', False),
])
def test_contains_works_on_arrays(left, op, right, result, render):
    assert render == result

def test_or_condition(op_compare, op_logical):
    opc = op_compare(1, '==', 2)
    assert opc.render({}, {}) == False
    opc = op_logical(opc, 'or', op_compare(2, '==', 1))
    assert opc.render({}, {}) == False
    opc = op_logical(opc, 'or', op_compare(1, '==', 1))
    assert opc.render({}, {}) == True

def test_and_condition(op_compare, op_logical):
    opc = op_compare(1, '==', 1)
    assert opc.render({}, {}) == True
    opc = op_logical(opc, 'and', op_compare(2, '==', 2))
    assert opc.render({}, {}) == True
    opc = op_logical(opc, 'and', op_compare(2, '==', 1))
    assert opc.render({}, {}) == False


def test_left_or_right_may_contain_operators(op_compare):
    context = {
        'one': "gnomeslab-and-or-liquid",
        'another': "gnomeslab-and-or-liquid"
    }
    opc = op_compare(TagSegmentVar('one'), '==', TagSegmentVar('another'))
    assert opc.render(context, {})
