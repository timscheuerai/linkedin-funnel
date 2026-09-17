"""Minimal native Excalidraw elements. No renderer or brand dependency."""
import random
import time


class Scene:
    def __init__(self):
        self.els = []
        self._count = 0
        self._random = random.Random(11)

    def base(self, kind, x, y, width, height, **kwargs):
        self._count += 1
        element = dict(id=f'{kind}-{self._count}', type=kind, x=x, y=y,
            width=width, height=height, angle=0, strokeColor='#707070',
            backgroundColor='transparent', fillStyle='solid', strokeWidth=1,
            strokeStyle='solid', roughness=0, opacity=100, groupIds=[], frameId=None,
            roundness=None, seed=self._random.randint(1, 10**9), version=1,
            versionNonce=self._random.randint(1, 10**9), isDeleted=False,
            boundElements=[], updated=int(time.time()*1000), link=None, locked=False)
        element.update(kwargs)
        return element

    def add(self, element):
        self.els.append(element)
        return element

    def text(self, x, y, value, size=22, color='#202020', family=2):
        # Estimate for authoring only; measure actual glyphs in the renderer.
        lines = value.split('\n')
        return self.add(self.base('text', x, y,
            max(map(len, lines), default=0)*size*0.55, len(lines)*size*1.25,
            text=value, originalText=value, fontSize=size, fontFamily=family,
            textAlign='left', verticalAlign='top', containerId=None,
            lineHeight=1.25, autoResize=True, strokeColor=color, baseline=size))

    def arrow(self, x1, y1, x2, y2, a=None, b=None, mid=None,
              color='#707070', dashed=False, width=2, head='arrow'):
        points = [[0, 0]] + [[x-x1, y-y1] for x, y in (mid or [])] + [[x2-x1, y2-y1]]
        arrow = self.add(self.base('arrow', x1, y1,
            max(p[0] for p in points)-min(p[0] for p in points),
            max(p[1] for p in points)-min(p[1] for p in points),
            points=points, startArrowhead=None, endArrowhead=head, elbowed=False,
            strokeStyle='dashed' if dashed else 'solid', strokeWidth=width,
            strokeColor=color,
            startBinding=dict(elementId=a['id'], focus=0, gap=4) if a else None,
            endBinding=dict(elementId=b['id'], focus=0, gap=4) if b else None))
        for node in (a, b):
            if node is not None:
                node['boundElements'].append(dict(id=arrow['id'], type='arrow'))
        return arrow

    def frame(self, x, y, width, height, name):
        return self.add(self.base('frame', x, y, width, height, name=name))

    def doc(self, source):
        return dict(type='excalidraw', version=2, source=source, elements=self.els,
                    appState=dict(viewBackgroundColor='#fafafa', gridSize=None),
                    files={})
