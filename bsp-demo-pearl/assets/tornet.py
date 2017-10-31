import random
import sys
from contextlib import contextmanager


def prop(a, b, p):
    return a + (b-a)*p


class Diagram(object):
    margin_width = 300
    margin_height = 10
    node_radius = 5
    padding = 32
    primary_color = '#7d4698' # tor purple
    secondary_color = '#abcd03' # tor green
    node_colors = ['red', 'green', 'blue', 'gold']

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.nodes = []
        self.f = None
        self.circuit = None

    def point_prop(self, px, py):
        x = prop(
                self.margin_width + self.padding,
                self.w - self.margin_width - self.padding,
                px,
                )
        y = prop(
                self.margin_height + self.padding,
                self.h - self.margin_height - self.padding,
                py,
                )
        return x, y

    def generate_random_node(self):
        return self.point_prop(random.random(), random.random())

    def draw_random_node(self):
        self.nodes.append(self.generate_random_node())

    def draw_random_nodes(self, n):
        for i in range(n):
            self.draw_random_node()

    def attrs(self, **kwargs):
        tags = ['{}="{}"'.format(k.replace('_', '-'), v) for k, v in kwargs.items()]
        return ' '.join(tags)

    def tag(self, name, **kwargs):
        self.write('\t<{name} {tags} />'.format(name=name, tags=self.attrs(**kwargs)))

    def embed_svg(self, name, x=0, y=0, scale=1.0):
        with open(name + '.svg') as s:
            svg = s.read()
        self.write('<g transform="translate({x},{y}) scale({scale},{scale})">'.format(
                scale=scale, x=x, y=y))
        self.write(svg)
        self.write('</g>')

    def text(self, txt, **attrs):
        attrs['font_family'] = 'monospace'
        self.write('<text {attrs}>{txt}</text>'.format(
                attrs=self.attrs(**attrs),
                txt=txt,
                ))

    def write(self, x):
        print >>self.f, x

    def base(self):
        self.tag('rect',
                x=self.margin_width,
                y=self.margin_height,
                width=self.w - 2*self.margin_width,
                height=self.h - 2*self.margin_height,
                fill=self.primary_color,
                fill_opacity=0.25,
                )

        for x, y in self.nodes:
            self.tag('circle', cx=x, cy=y, r=self.node_radius,
                    fill='black',
                    fill_opacity=0.4,
                    )

        self.embed_svg('gopher-side-right',
                y=(self.h - self.margin_width) / 2,
                scale=0.5,
                )

        self.write('<g opacity="0.5">')
        x=self.w - self.margin_width * 0.7
        y=(self.h - self.margin_width) / 2
        self.embed_svg('gopher-side-right-path',
                scale=0.5,
                x=x, y=y,
                )
        self.text('?', font_size=170, x=x+65, y=y+200)
        self.write('</g>')

        self.embed_svg('torlogo',
                scale=0.7,
                x=self.margin_width + self.padding,
                y=self.margin_height + self.padding,
                )

    def set_circuit(self, props):
        self.circuit = [self.point_prop(px, py) for px, py in props]

    def draw_full_circuit(self):
        for i in range(len(self.circuit)+1):
            self.draw_circuit_hop(i)
        self.draw_circuit_nodes()

    def circuit_point(self, i):
        points = (
                [(self.margin_width-100,self.h/2)] +
                self.circuit +
                [(self.w-self.margin_width+100, self.h/2)]
                )
        return points[i]

    def draw_circuit_hop(self, idx):
        p, q = self.circuit_point(idx), self.circuit_point(idx+1)
        self.tag('path',
                d='M {} {} L {} {}'.format(p[0], p[1], q[0], q[1]),
                stroke=self.secondary_color,
                stroke_width=8,
                fill='transparent',
                )

    def draw_circuit_nodes(self):
        for i, coords in enumerate(self.circuit):
            x, y = coords
            self.tag('circle', cx=x, cy=y, r=self.node_radius*1.5,
                    fill=self.node_colors[i],
                    fill_opacity=0.9,
                    )

    def hop_point(self, i):
        p, q = self.circuit_point(i), self.circuit_point(i+1)
        return ((p[0] + q[0])/2.0, (p[1] + q[1])/2.0)

    def draw_cell_for_hop(self, on, dst, scale=3.0):
        x, y = self.hop_point(on)
        for i in range(on, dst):
            self.tag('circle',
                    cx=x, cy=y,
                    r=scale*self.node_radius*(dst - i),
                    fill=self.node_colors[i],
                    )

    @contextmanager
    def output_to_file(self, filename):
        with open(filename, 'w') as f:
            self.f = f
            self.write('<svg width="{w}" height="{h}" version="1.1" xmlns="http://www.w3.org/2000/svg">'.format(
                w=self.w, h=self.h,
                ))
            yield
            self.write('</svg>')
            self.f = None


def main():
    d = Diagram(1200, 600)
    d.draw_random_nodes(1<<8)
    d.set_circuit([
        (0.2, 0.4),
        (0.5,  0.66),
        (0.75, 0.3),
        ])

    with d.output_to_file('tornet-blank.svg'):
        d.base()

    with d.output_to_file('tornet-circuit.svg'):
        d.base()
        d.draw_full_circuit()

    with d.output_to_file('tornet-create.svg'):
        d.base()
        d.draw_circuit_hop(0)
        d.draw_circuit_nodes()

    with d.output_to_file('tornet-extend.svg'):
        d.base()
        d.draw_circuit_hop(0)
        d.draw_circuit_hop(1)
        d.draw_circuit_nodes()
        d.draw_cell_for_hop(0, 2)

    with d.output_to_file('tornet-extend2.svg'):
        d.base()
        d.draw_circuit_hop(0)
        d.draw_circuit_hop(1)
        d.draw_circuit_hop(2)
        d.draw_circuit_nodes()
        d.draw_cell_for_hop(1, 3)

    for i in range(0, 4):
        filename = 'tornet-data{}.svg'.format(i)
        with d.output_to_file(filename):
            d.base()
            d.draw_full_circuit()
            d.draw_cell_for_hop(i, 4)

if __name__ == '__main__':
    main()
