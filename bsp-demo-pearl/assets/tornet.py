import random
import sys


def uniform_part(a, b, i, n):
    w = (b - a) / float(n)
    return random.uniform(a + i*w, a + (i+1)*w)


class Diagram(object):
    margin_width = 300
    margin_height = 10
    node_radius = 5
    padding = 32
    primary_color = '#7d4698' # tor purple
    secondary_color = '#abcd03' # tor green

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.nodes = []
        self.circuit = None

    def generate_random_node(self, i=0, n=1):
        x = uniform_part(
                self.margin_width + self.padding,
                self.w - self.margin_width - self.padding,
                i, n,
                )
        y = uniform_part(
                self.margin_height + self.padding,
                self.h - self.margin_height - self.padding,
                i, n,
                )
        return x, y

    def draw_random_node(self):
        self.nodes.append(self.generate_random_node())

    def draw_random_nodes(self, n):
        for i in range(n):
            self.draw_random_node()

    def add_circuit(self, n):
        self.circuit = [self.generate_random_node(i, n) for i in range(n)]

    def attrs(self, **kwargs):
        tags = ['{}="{}"'.format(k.replace('_', '-'), v) for k, v in kwargs.items()]
        return ' '.join(tags)

    def tag(self, f, name, **kwargs):
        print >>f, '\t<{name} {tags} />'.format(name=name, tags=self.attrs(**kwargs))

    def embed_svg(self, f, name, x=0, y=0, scale=1.0):
        with open(name + '.svg') as s:
            svg = s.read()
        print >>f, '<g transform="translate({x},{y}) scale({scale},{scale})">'.format(
                scale=scale, x=x, y=y)
        print >>f, svg
        print >>f, '</g>'

    def text(self, f, txt, **attrs):
        attrs['font_family'] = 'monospace'
        print >>f, '<text {attrs}>{txt}</text>'.format(
                attrs=self.attrs(**attrs),
                txt=txt,
                )

    def output(self, f):
        print >>f, '<svg width="{w}" height="{h}" version="1.1" xmlns="http://www.w3.org/2000/svg">'.format(
                w=self.w, h=self.h,
                )

        self.tag(f, 'rect',
                x=self.margin_width,
                y=self.margin_height,
                width=self.w - 2*self.margin_width,
                height=self.h - 2*self.margin_height,
                fill=self.primary_color,
                fill_opacity=0.25,
                )

        for x, y in self.nodes:
            self.tag(f, 'circle', cx=x, cy=y, r=self.node_radius,
                    fill='black',
                    fill_opacity=0.4,
                    )

        self.embed_svg(f, 'gopher-side-right',
                y=(self.h - self.margin_width) / 2,
                scale=0.5,
                )

        print >>f, '<g opacity="0.5">'
        x=self.w - self.margin_width * 0.7
        y=(self.h - self.margin_width) / 2
        self.embed_svg(f, 'gopher-side-right-path',
                scale=0.5,
                x=x, y=y,
                )
        self.text(f, '?', font_size=170, x=x+65, y=y+200)
        print >>f, '</g>'

        self.embed_svg(f,
                'torlogo',
                scale=0.7,
                x=self.margin_width + self.padding,
                y=self.margin_height + self.padding,
                )

        if self.circuit:
            points = (
                    [(self.margin_width-100,self.h/2)] +
                    self.circuit +
                    [(self.w-self.margin_width+100, self.h/2)]
                    )
            path = 'M ' + ' L '.join(['{} {}'.format(x, y) for x, y in points])
            self.tag(f, 'path',
                    d=path,
                    stroke=self.secondary_color,
                    stroke_width=8,
                    fill='transparent',
                    )
            for x, y in self.circuit:
                self.tag(f, 'circle', cx=x, cy=y, r=self.node_radius*1.5,
                        fill='red',
                        fill_opacity=0.7,
                        )

        print >>f, '</svg>'

    def output_to_file(self, filename):
        with open(filename, 'w') as f:
            self.output(f)


def main():
    random.seed(850)

    d = Diagram(1200, 600)
    d.draw_random_nodes(1<<8)
    d.output_to_file('tornet-blank.svg')
    d.add_circuit(3)
    d.output_to_file('tornet-circuit.svg')


if __name__ == '__main__':
    main()
