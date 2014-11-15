from ascii_drawing import *

pict = """\
############            llllllllllll@@@@@@@@@@@@..........
############            llllllllllll@@@@@@@@@@@@..........
############            llllllllllll@@@@@@@@@@@@..........
############            llllllllllll@@@@@@@@@@@@..........
############            llllllllllll@@@@@@@@@@@@..........
############            llllllllllll@@@@@@@@@@@@..........
############            llllllllllll@@@@@@@@@@@@..........
            ############llllllllllll@@@@@@@@@@@@..........
            ############llllllllllll@@@@@@@@@@@@..........
            ############llllllllllll@@@@@@@@@@@@..........
            ############llllllllllll@@@@@@@@@@@@..........
            ############llllllllllll@@@@@@@@@@@@..........
            ############llllllllllll@@@@@@@@@@@@..........
            ############llllllllllll@@@@@@@@@@@@..........
"""

def test_figure_from_string():
    f = figure_from_string(pict)
    h = 14
    w = 29
    print f
    assert f.get_height() == h
    assert f.get_width() == w

    f2 = figure_from_string(repr(f), chars_per_pixar=(5, 2))
    print f2
    assert f2.get_height() == 3
    assert f2.get_width() == 15

    f3 = figure_from_string(pict, chars_per_pixar=(1,1))
    print f3
    assert f3.get_height() == h
    assert f3.get_width() == 2 * w
    assert repr(f3) == pict

def test_scale_conversor():
    f = figure_from_string(pict, chars_per_pixar=(1,2))
    h = 14
    w = 29
    assert f.get_height() == h
    assert f.get_width() == w
    sc = ScaleConversor(3 * h, 2 * w)
    f2 = sc.convert(f)
    f3 = ScaleConversor(h, 2 * w).convert(f2)
    print f
    print f2
    print f3
    assert repr(f3) == pict
    c = Canvas(14, 29)
    c.add_figure(ScaleConversor(h, w).convert(f3), 0, 0)
    assert c.paint() == pict

