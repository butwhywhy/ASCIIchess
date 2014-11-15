
class Figure(object):

    def __init__(self):
        pass

    def pixar(self, y, x):
        ''' A couple of doubles representing darkness and opacity '''
        raise Exception("Subclasses must implement this method")

    def get_height(self):
        raise Exception("Subclasses must implement this method")

    def get_width(self):
        raise Exception("Subclasses must implement this method")

class PixByPixFigure(Figure):

    def __init__(self, pix_matrix):
        self.pix_matrix = pix_matrix

    def pixar(self, y, x):
        return self.pix_matrix[y][x]

    def get_height(self):
        return len(self.pix_matrix)

    def get_width(self):
        return len(self.pix_matrix[0])

    def fill(self, darkness):
        self.pix_matrix = [[darkness for j in xrange(width)] for i in xrange(height)]

    def __repr__(self):
        s = ''
        for i in xrange(self.get_height()):
            for j in xrange(self.get_width()):
                s = s + darkness_to_ascii(self.pixar(i, j)[0])
            s = s + '\n'
        return s



ASCI_DEFAULT = (' ', '.', ':', ';', 'l', '=', '+', '*', 'T', '8', '#', '@')
CHARS_PER_PIXAR_DEFAULT = (1, 2)

class Canvas(PixByPixFigure):

    def __init__(self, height, width, ascii_scale=ASCI_DEFAULT, chars_per_pixar=CHARS_PER_PIXAR_DEFAULT):
        pix_matrix = [[(0., 1) for j in xrange(width)] for i in xrange(height)]
        super(Canvas, self).__init__(pix_matrix)
        self.ascii_scale = ascii_scale
        self.chars_per_pixar = chars_per_pixar

    def set_ascii_scale(self, ascii_scale):
        self.ascii_scale = ascii_scale

    def set_chars_per_pixar(self, chars_y, chars_x):
        self.chars_per_pixar = (chars_y, chars_x);

    def add_figure(self, figure, y, x):
        for i in xrange(figure.get_height()):
            for j in xrange(figure.get_width()):
                dark_base = self.pix_matrix[y + i][x + j][0]
                (dark_figure, opacity) = figure.pixar(i, j)
                self.pix_matrix[y + i][x + j] = (dark_figure * opacity 
                        + dark_base * (1 - opacity), 1)

    def paint(self):
        s = ''''''
        for i in xrange(self.get_height()):
            line = ''
            for j in xrange(self.get_width()):
                ascii_char = darkness_to_ascii(self.pix_matrix[i][j][0], self.ascii_scale)
                for k in xrange(self.chars_per_pixar[1]):
                    line = line + ascii_char
            for j in xrange(self.chars_per_pixar[0]):
                s = s + line + '\n'
        return s


def darkness_to_ascii(darkness, ascii_scale=ASCI_DEFAULT):
    n = len(ascii_scale) - 1
    index = int(round(n * darkness))
    return ascii_scale[index]

def ascii_to_darkness(char, ascii_scale=ASCI_DEFAULT):
    n = len(ascii_scale) - 1
    try:
        return ascii_scale.index(char)/float(n)
    except ValueError, e:
        print char
        raise e


class Square(Figure):
    
    def __init__(self, height, width, darkness=1, opacity=1):
        self.height = height
        self.width = width
        self.darkness = darkness
        self.opacity = opacity

    def inside(self, y, x):
        return x >= 0 and y >= 0 and x < self.width and y < self.height

    def pixar(self, y, x):
        return (self.darkness, self.opacity) if self.inside(y, x) else (0, 0)

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

def figure_from_string(string, ascii_scale=ASCI_DEFAULT, chars_per_pixar=CHARS_PER_PIXAR_DEFAULT, line_separator=None):
    if line_separator is None:
        from os import linesep
        line_separator = linesep
    y_scale, x_scale = chars_per_pixar
    chars_in_pixar = float(x_scale * y_scale)
    rows = string.split(linesep)

    str_height = len(rows)
    if len(rows[str_height - 1]) == 0:
        str_height -= 1
    height = str_height / y_scale
    if str_height % y_scale:
        height += 1

    str_width = max(len(row) for row in rows)
    width = str_width / x_scale
    if str_width % x_scale:
        width += 1

    pixars = [[(0., 1) for j in xrange(width)] for i in xrange(height)]
    for pix_y in xrange(height):
        y_from = pix_y * y_scale
        y_to = min(y_from + y_scale, str_height)
        for pix_x in xrange(width):
            dark_sum = 0
            for i in xrange(y_from, y_to):
                x_from = min(pix_x * x_scale, len(rows[i]))
                x_to = min(x_from + x_scale, len(rows[i]))
                for j in xrange(x_from, x_to):
                    dark_sum += ascii_to_darkness(rows[i][j], ascii_scale)
            pixars[pix_y][pix_x] = (dark_sum/chars_in_pixar, 1)

    return PixByPixFigure(pixars)

def figure_from_file(file_path, ascii_scale=ASCI_DEFAULT, 
        chars_per_pixar=CHARS_PER_PIXAR_DEFAULT, line_separator=None):
    with open(file_path) as f:
        return figure_from_string(f.read(), ascii_scale,
                chars_per_pixar, line_separator)


class Conversor(object):

    def convert(self, figure):
        raise Exception("Subclasses must implement this method")

class GeneralColorConversor(Conversor):

    def __init__(self, pix_transformation):
        self.transform = pix_transformation

    def convert(self, figure):
        pix_matrix = [
                [self.transform(*figure.pixar(y, x)) 
            for x in xrange(figure.get_width())] 
            for y in xrange(figure.get_height())]
        return PixByPixFigure(pix_matrix)

class SingleColorConversor(GeneralColorConversor):

    def __init__(self, from_darkness=(0, 1), from_opacity=(0, 1), 
            to_darkness=None, to_opacity=None):
        self.from_darkness = from_darkness
        self.from_opacity = from_opacity
        self.to_darkness = to_darkness
        self.to_opacity = to_opacity

        def in_range(value, value_range):
            if value == value_range:
                return True
            try:
                if value >= value_range[0] and value <= value_range[1]:
                    return True
            except TypeError, e:
                pass
            return False

        def transform_pix(darkness, opacity):
            new_d = darkness
            new_o = opacity
            if (in_range(darkness, self.from_darkness) 
                    and in_range(opacity, self.from_opacity)):
                if self.to_darkness is not None:
                    new_d = self.to_darkness
                if self.to_opacity is not None:
                    new_o = self.to_opacity
            return (new_d, new_o)

        super(SingleColorConversor, self).__init__(transform_pix)

def perc(float0, float1, maximum):
    from math import floor
    i0 = int(floor(float0))
    if i0 < 0:
        i0 = 0
    r0 = float0 - i0 
    i1 = int(floor(float1))
    if i1 > maximum:
        i1 = maximum
    r0 = float1 - i1
    if i0 == i1:
        yield (i0, float1 - float0)
    else:
        yield (i0, i0 + 1 - float0)
        for integer in xrange(i0 + 1, i1):
            yield (integer, 1.)
        yield (i1, float1 - i1)

class ScaleConversor(Conversor):

    def __init__(self, height, width):
        self.height = height
        self.width = width

    def convert(self, figure):
        x_scale = figure.get_width()/float(self.width)
        y_scale = figure.get_height()/float(self.height)
        pix_matrix = []
        for i in xrange(self.height):
            y0 = i * y_scale
            y1 = y0 + y_scale
            pix_line = []
            for j in xrange(self.width):
                x0 = j * x_scale
                x1 = x0 + x_scale
                (darkness, opacity) = (0,0)
                for (y, perc_y) in perc(y0, y1, figure.get_height() - 1):
                    for (x, perc_x) in perc(x0, x1, figure.get_width() - 1):
                        try:
                            darkness += figure.pixar(y, x)[0] * perc_x * perc_y
                            opacity += figure.pixar(y, x)[1] * perc_x * perc_y
                        except Exception, e:
                            print y, x, figure.pixar(y, x)
                            raise e
                darkness /= x_scale * y_scale
                opacity /= x_scale * y_scale
                pix_line.append((darkness, opacity))
            pix_matrix.append(pix_line)
        return PixByPixFigure(pix_matrix)

