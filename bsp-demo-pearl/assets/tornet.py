import random


class Diagram(object):
    margin_width = 300
    margin_height = 10
    node_radius = 5
    padding = 32
    primary_color = '#7d4698' # tor purple

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.nodes = []

    def draw_random_node(self):
        x = random.uniform(
                self.margin_width + self.padding,
                self.w - self.margin_width - self.padding,
                )
        y = random.uniform(
                self.margin_height + self.padding,
                self.h - self.margin_height - self.padding,
                )
        self.nodes.append((x, y))

    def draw_random_nodes(self, n):
        for i in range(n):
            self.draw_random_node()

    def attrs(self, **kwargs):
        tags = ['{}="{}"'.format(k.replace('_', '-'), v) for k, v in kwargs.items()]
        return ' '.join(tags)

    def tag(self, name, **kwargs):
        print '\t<{name} {tags} />'.format(name=name, tags=self.attrs(**kwargs))

    def embed_svg(self, name, x=0, y=0, scale=1.0):
        with open(name + '.svg') as f:
            svg = f.read()
        print '<g transform="translate({x},{y}) scale({scale},{scale})">'.format(
                scale=scale, x=x, y=y)
        print svg
        print '</g>'

    def output(self):
        print '<svg width="{w}" height="{h}" version="1.1" xmlns="http://www.w3.org/2000/svg">'.format(
                w=self.w, h=self.h,
                )

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
                    fill_opacity=0.5,
                    )

        self.embed_svg('gopher-side-right',
                y=(self.h - self.margin_width) / 2,
                scale=0.5,
                )

        self.embed_svg(
                'torlogo',
                scale=0.7,
                x=self.margin_width + self.padding,
                y=self.margin_height + self.padding,
                )

        print '</svg>'


def main():
    d = Diagram(1200, 600)
    d.draw_random_nodes(1<<8)
    d.output()


if __name__ == '__main__':
    main()
