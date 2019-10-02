import operator
import pytest

import nightcore


class Input(nightcore.RelativeChange):
    def as_percent(self):
        return float(self.amount)


class TestRelativeChange:
    def test_amount_is_set(self):
        assert Input(123).amount == 123

    def test_unary_negative(self):
        assert (-Input(+123)).amount == -123

    def test_unary_positive(self):
        assert (+Input(-123)).amount == 123

    @pytest.mark.parametrize("op, rhs, expected", (
        (operator.eq, 0, False),
        (operator.eq, 1, True),
        (operator.eq, 2, False),
        (operator.eq, Input(0), False),
        (operator.eq, Input(1), True),
        (operator.eq, Input(2), False),

        (operator.lt, 0, False),
        (operator.lt, 1, False),
        (operator.lt, 2, True),
        (operator.lt, Input(0), False),
        (operator.lt, Input(1), False),
        (operator.lt, Input(2), True),

        (operator.le, 0, False),
        (operator.le, 1, True),
        (operator.le, 2, True),
        (operator.le, Input(0), False),
        (operator.le, Input(1), True),
        (operator.le, Input(2), True),

        (operator.gt, 0, True),
        (operator.gt, 1, False),
        (operator.gt, 2, False),
        (operator.gt, Input(0), True),
        (operator.gt, Input(1), False),
        (operator.gt, Input(2), False),

        (operator.ge, 0, True),
        (operator.ge, 1, True),
        (operator.ge, 2, False),
        (operator.ge, Input(0), True),
        (operator.ge, Input(1), True),
        (operator.ge, Input(2), False),
    ))
    def test_comparison(self, op, rhs, expected):
        assert op(Input(1), rhs) == expected

    def test_float_use_as_percent(self):
        class Test(nightcore.RelativeChange):
            flag = False

            def as_percent(self):
                self.flag = True
                return 1.0

        instance = Test(123)
        assert not instance.flag
        assert float(instance) == 1.0
        assert instance.flag

    def test_int(self):
        assert int(Input(1.1)) == 1


class Cents(nightcore.BaseInterval):
    n_per_octave = 1200


class TestBaseIntervalSubclasses:
    @pytest.mark.parametrize("interval, expected", (
        (nightcore.Semitones, 100),
        (nightcore.Tones, 200),
        (nightcore.Octaves, 1200),
    ))
    def test_cents_per_interval_correct(self, interval, expected):
        assert Cents.n_per_octave / interval.n_per_octave == expected

    @pytest.mark.parametrize("op", (
        operator.add,
        operator.sub,
        operator.mul,
        operator.truediv,
        operator.floordiv,
        operator.mod,
    ))
    def test_reverse_op_fails(self, op):
        with pytest.raises(TypeError):
            op(123, Cents(123))

    @pytest.mark.parametrize("op", (
        operator.add,
        operator.sub,
        operator.mul,
        operator.truediv,
        operator.floordiv,
        operator.mod,
    ))
    def test_arithmetic_on_same_type(self, op):
        assert op(Cents(123), Cents(2)) == Cents(op(123, 2))

    @pytest.mark.parametrize("op", (
        operator.add,
        operator.sub,
        operator.mul,
        operator.truediv,
        operator.floordiv,
        operator.mod,
    ))
    @pytest.mark.parametrize("interval", (
        nightcore.Semitones,
        nightcore.Tones,
        nightcore.Octaves,
    ))
    def test_arithmetic_on_different_subclasses(self, op, interval):
        cents_per_interval = Cents.n_per_octave / interval.n_per_octave
        expected = Cents(op(123, cents_per_interval))
        assert op(Cents(123), interval(1)) == expected

    @pytest.mark.parametrize("op", (
        operator.add,
        operator.sub,
        operator.mul,
        operator.truediv,
        operator.floordiv,
        operator.mod,
    ))
    def test_arithmetic_on_rhs_numbers(self, op):
        return op(Cents(123), 4) == Cents(op(123, 4))


class TestPercent:
    def test_reverse_add(self):
        assert 2 + nightcore.Percent(50) == 3.0

    def test_reverse_sub(self):
        assert 2 - nightcore.Percent(50) == 1.0

    @pytest.mark.parametrize("op", (
        operator.add,
        operator.sub,
        operator.mul,
        operator.truediv,
        operator.floordiv,
        operator.mod,
    ))
    def test_arithmetic(self, op):
        assert op(nightcore.Percent(50), 2) == nightcore.Percent(op(50, 2))

    @pytest.mark.parametrize("op", (
        operator.mul,
        operator.truediv,
        operator.floordiv,
        operator.mod,
    ))
    def test_reverse_arithmetic(self, op):
        fifty = nightcore.Percent(50)
        assert op(2, fifty) == op(2, fifty.as_percent())
