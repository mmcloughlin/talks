from contextlib import contextmanager
import random
import math


SERVER_CONN, CLIENT_CONN = range(2)



class Diagram(object):
    weight = 8
    conn_color = {
            SERVER_CONN: 'blue',
            CLIENT_CONN: 'green',
            }

    def __init__(self, d):
        self.w = d
        self.h = d
        self.conns = []
        self.conns_by_type = {}

    def attrs(self, **kwargs):
        tags = ['{}="{}"'.format(k.replace('_', '-'), v) for k, v in kwargs.items()]
        return ' '.join(tags)

    def tag(self, name, **kwargs):
        self.write('\t<{name} {tags} />'.format(name=name, tags=self.attrs(**kwargs)))

    def write(self, x):
        print >>self.f, x

    def add_conn(self, typ):
        angle = 360.0 * random.random()
        self.conns.append((typ, angle))
        self.conns_by_type.setdefault(typ, []).append(angle)

    def radius(self):
        return self.w*0.12

    def polar(self, r, angle):
        x = self.w/2 + r * math.cos(angle)
        y = self.h/2 + r * math.sin(angle)
        return x, y

    def base(self):
        for typ, angle in self.conns:
            fx, fy = self.polar(self.radius(), angle)
            tx, ty = self.polar(self.w/2, angle)
            self.tag('path',
                    d='M {} {} L {} {}'.format(fx, fy, tx, ty),
                    stroke=self.conn_color[typ],
                    stroke_width=2*self.weight,
                    fill='transparent',
                    stroke_opacity=0.5,
                    )

        self.tag('circle',
                cx=self.w/2, cy=self.w/2,
                r=self.radius(),
                stroke='grey',
                stroke_width=2*self.weight,
                fill='transparent',
                )

    def draw_traffic(self, src_angle, dst_angle):
        def line(t, coords):
            return ' '.join(map(str, [t] + list(coords)))
        d  = line('M', self.polar(self.w/2, src_angle))
        d += line('L', self.polar(self.radius(), src_angle))
        d += line('L', self.polar(self.radius(), dst_angle))
        d += line('L', self.polar(self.w/2, dst_angle))
        self.tag('path',
                d=d,
                stroke='red',
                stroke_width=0.7*self.weight,
                fill='transparent',
                stroke_opacity=0.7,
                )

    def random_server_angle(self):
        return random.choice(self.conns_by_type[SERVER_CONN])

    def random_client_angles(self, n):
        return random.sample(self.conns_by_type[CLIENT_CONN], n)

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
    random.seed(2)

    d = Diagram(800)

    num_server = 5
    num_client = 7

    for _ in range(num_server):
        d.add_conn(SERVER_CONN)
    for _ in range(num_client):
        d.add_conn(CLIENT_CONN)

    with d.output_to_file('crux.svg'):
        d.base()

    server = d.random_server_angle()
    clients = d.random_client_angles(num_client)
    for n in range(1, num_client):
        filename = 'crux-circuits{}.svg'.format(n)
        with d.output_to_file(filename):
            d.base()
            for c in clients[:n]:
                d.draw_traffic(server, c)

if __name__ == '__main__':
    main()
