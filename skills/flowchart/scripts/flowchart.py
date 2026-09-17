"""Editable, self-contained flowchart primitives with a neutral default theme.

No scene is built on import. Construct one Flowchart per diagram.
"""
import base64
import hashlib
import importlib.util
import json
import math
import mimetypes
from pathlib import Path


class Flowchart:
    def __init__(self, theme=None, font_family=2, center_x=920):
        path = Path(__file__).with_name('primitives.py')
        spec = importlib.util.spec_from_file_location('_flowchart_primitives', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.scene = module.Scene()
        self._base = self.scene.base
        self.font_family = font_family
        self.center_x = center_x
        self.groups = []
        self.image_files = {}
        colors = dict(canvas='#fafafa', surface='#ffffff', muted='#f1f1f1',
                      text='#202020', accent='#383838', secondary='#606060',
                      connector='#707070', border='#cccccc', tint='#eeeeee')
        if theme:
            unknown = set(theme) - set(colors)
            if unknown:
                raise ValueError(f'Unknown theme roles: {sorted(unknown)}')
            colors.update(theme)
        for name, value in colors.items():
            setattr(self, name.upper(), value)

    def add(self, e):
        e['groupIds'] = list(self.groups)
        return self.scene.add(e)

    def text(self, x, y, value, size=22, color=None, center=False):
        if color is None:
            color = self.TEXT
        e = self.scene.text(x, y, value, size=size, color=color, family=self.font_family)
        if center:
            e['x'] -= e['width'] / 2
            e['textAlign'] = 'center'
        e['groupIds'] = list(self.groups)
        return e

    def box(self, x, y, w, h, fill=None, stroke=None, kind='rectangle', dashed=False, rounded=False):
        if fill is None:
            fill = self.SURFACE
        if stroke is None:
            stroke = self.CONNECTOR
        return self.add(self._base(kind, x, y, w, h, backgroundColor=fill, strokeColor=stroke, strokeWidth=1.5, strokeStyle='dashed' if dashed else 'solid', roundness={'type': 3} if rounded else None))

    def node(self, key, x, y, w, h, title, body=None, kind='card', size=22):
        self.groups.insert(0, key)
        fill = {'file': self.MUTED, 'function': self.TINT, 'skill': self.TEXT}.get(kind, self.SURFACE)
        shape = self.box(x, y, w, h, fill=fill, stroke=self.ACCENT if kind == 'function' else self.TEXT if kind == 'skill' else self.CONNECTOR, dashed=kind == 'step', rounded=kind == 'skill')
        shape['customData'] = dict(nodeKind=kind)
        if kind == 'function':
            shape['strokeWidth'] = 2
        self.text(x + w / 2, y + (14 if body else (h - size * 1.25) / 2), title, size=size, color=self.CANVAS if kind == 'skill' else self.TEXT, center=True)
        if body:
            self.text(x + w / 2, y + 45, body, size=18, color=self.CANVAS if kind == 'skill' else self.SECONDARY, center=True)
        self.groups.pop(0)
        return shape

    def arrow(self, points, color=None, dashed=False, width=2, head='arrow', a=None, b=None):
        if color is None:
            color = self.CONNECTOR
        e = self.scene.arrow(*points[0], *points[-1], a=a, b=b, mid=points[1:-1], color=color, dashed=dashed, width=width, head=head)
        e['width'] = max((p[0] for p in points)) - min((p[0] for p in points))
        e['height'] = max((p[1] for p in points)) - min((p[1] for p in points))
        e['groupIds'] = list(self.groups)
        return e

    def stage(self, key, y, h, top, bottom, title):
        self.groups.insert(0, key)
        inset = (top - bottom) / 2
        self.add(self._base('line', self.center_x - top / 2, y, top, h, points=[[0, 0], [top, 0], [top - inset, h], [inset, h], [0, 0]], backgroundColor=self.SURFACE, strokeColor=self.CONNECTOR, strokeWidth=1.5, startArrowhead=None, endArrowhead=None))
        self.text(self.center_x, y + 20, title, size=28, center=True)

    def end_stage(self):
        self.groups.pop(0)

    def gate(self, key, x, y, w, h, label):
        self.groups.insert(0, key)
        e = self.box(x, y, w, h, kind='diamond', fill=self.SURFACE, stroke=self.ACCENT)
        e['customData'] = dict(nodeKind='decision')
        lines = label.count('\n') + 1
        self.text(x + w / 2, y + (h - lines * 17 * 1.25) / 2, label, size=17, color=self.ACCENT, center=True)
        self.groups.pop(0)
        return e

    def rule(self, x1, y, x2, color=None):
        if color is None:
            color = self.BORDER
        return self.add(self._base('line', x1, y, x2 - x1, 0, points=[[0, 0], [x2 - x1, 0]], strokeColor=color, strokeWidth=1, startArrowhead=None, endArrowhead=None))

    def icon(self, name, x, y, size=36, color=None):
        if color is None:
            color = self.ACCENT
        'Small semantic line icons, built from editable native Excalidraw shapes.'
        self.groups.insert(0, f'icon-{name}-{len(self.scene.els)}')
        first = len(self.scene.els)
        scale = size / 24

        def line(points):
            px, py = points[0]
            self.add(self._base('line', x + px * scale, y + py * scale, (max((p[0] for p in points)) - min((p[0] for p in points))) * scale, (max((p[1] for p in points)) - min((p[1] for p in points))) * scale, points=[[(a - px) * scale, (b - py) * scale] for a, b in points], strokeColor=color, strokeWidth=2, startArrowhead=None, endArrowhead=None))

        def rect(a, b, w, h):
            self.add(self._base('rectangle', x + a * scale, y + b * scale, w * scale, h * scale, strokeColor=color, strokeWidth=2))

        def circle(a, b, r):
            self.add(self._base('ellipse', x + (a - r) * scale, y + (b - r) * scale, 2 * r * scale, 2 * r * scale, strokeColor=color, strokeWidth=2))
        if name in ('company', 'company-enrich'):
            rect(4, 4, 12, 17)
            for a, b in ((7, 8), (12, 8), (7, 12), (12, 12)):
                line([(a, b), (a + 1, b)])
            line([(9, 21), (9, 17), (12, 17), (12, 21)])
            if name == 'company-enrich':
                line([(20, 3), (20, 11)])
                line([(17, 7), (23, 7)])
        elif name == 'score':
            circle(11, 12, 9)
            circle(11, 12, 5)
            line([(11, 12), (21, 2)])
            line([(16, 2), (21, 2), (21, 7)])
        elif name in ('person', 'person-search', 'person-enrich', 'person-score'):
            circle(9, 7, 4)
            line([(2, 21), (2, 18), (4, 14), (9, 13), (13, 14)])
            if name == 'person-search':
                circle(17, 17, 4)
                line([(20, 20), (23, 23)])
            elif name == 'person-enrich':
                line([(18, 13), (18, 21)])
                line([(14, 17), (22, 17)])
            elif name == 'person-score':
                line([(14, 18), (17, 21), (23, 14)])
            else:
                line([(13, 14), (16, 18), (16, 21)])
        elif name == 'brain':
            pts = [(12, 4), (10, 2), (7, 2), (5, 4), (5, 6), (2, 8), (2, 11), (3, 13), (2, 16), (4, 19), (7, 19), (8, 22), (10, 22), (12, 20), (12, 4)]
            line(pts)
            line([(24 - a, b) for a, b in pts])
            line([(5, 6), (8, 7), (8, 10)])
            line([(3, 13), (7, 13), (9, 16)])
            line([(19, 6), (16, 7), (16, 10)])
            line([(21, 13), (17, 13), (15, 16)])
        elif name == 'waterfall':
            rect(2, 2, 9, 5)
            rect(8, 10, 9, 5)
            rect(14, 18, 9, 5)
            line([(5, 8), (5, 12), (7, 12)])
            line([(11, 16), (11, 20), (13, 20)])
        elif name == 'verify':
            line([(12, 2), (21, 6), (20, 15), (17, 20), (12, 23), (7, 20), (4, 15), (3, 6), (12, 2)])
            line([(7, 12), (11, 16), (17, 9)])
        elif name == 'rank':
            line([(2, 6), (15, 6)])
            line([(2, 12), (11, 12)])
            line([(2, 18), (7, 18)])
            line([(20, 21), (20, 3)])
            line([(16, 7), (20, 3), (24, 7)])
        elif name == 'split':
            line([(12, 22), (12, 13), (4, 7), (4, 2)])
            line([(12, 13), (20, 7), (20, 2)])
            line([(1, 5), (4, 2), (7, 5)])
            line([(17, 5), (20, 2), (23, 5)])
        elif name == 'mail-ai':
            rect(2, 9, 19, 13)
            line([(2, 10), (11.5, 17), (21, 10)])
            line([(16, 1), (16, 7)])
            line([(13, 4), (19, 4)])
            line([(6, 2), (6, 6)])
            line([(4, 4), (8, 4)])
        elif name == 'send':
            line([(2, 10), (22, 2), (14, 22), (10, 14), (2, 10)])
            line([(10, 14), (22, 2)])
        elif name == 'chart':
            line([(3, 2), (3, 22), (23, 22)])
            line([(7, 17), (12, 12), (16, 14), (22, 5)])
        elif name == 'tools':
            line([(3, 7), (8, 12), (3, 17)])
            line([(12, 18), (21, 18)])
        elif name == 'microphone':
            rect(8, 2, 8, 13)
            line([(4, 10), (4, 14), (7, 18), (17, 18), (20, 14), (20, 10)])
            line([(12, 18), (12, 23)])
            line([(7, 23), (17, 23)])
        elif name == 'book':
            line([(12, 5), (7, 2), (2, 2), (2, 20), (7, 20), (12, 23), (17, 20), (22, 20), (22, 2), (17, 2), (12, 5), (12, 23)])
        elif name == 'calendar':
            rect(2, 5, 20, 18)
            line([(2, 10), (22, 10)])
            line([(7, 2), (7, 7)])
            line([(17, 2), (17, 7)])
            for a, b in ((7, 14), (12, 14), (17, 14), (7, 19), (12, 19)):
                line([(a, b), (a+1, b)])
        elif name == 'pen':
            line([(3, 21), (5, 14), (17, 2), (22, 7), (10, 19), (3, 21)])
            line([(14, 5), (19, 10)])
        elif name == 'message':
            line([(2, 3), (22, 3), (22, 18), (10, 18), (4, 23), (4, 18), (2, 18), (2, 3)])
            line([(6, 8), (18, 8)])
            line([(6, 13), (15, 13)])
        elif name == 'layers':
            line([(12, 2), (23, 8), (12, 14), (1, 8), (12, 2)])
            line([(2, 13), (12, 19), (22, 13)])
            line([(2, 18), (12, 24), (22, 18)])
        elif name == 'eye':
            line([(1, 12), (6, 6), (12, 4), (18, 6), (23, 12), (18, 18), (12, 20), (6, 18), (1, 12)])
            circle(12, 12, 4)
        elif name == 'file':
            line([(5, 2), (15, 2), (20, 7), (20, 22), (5, 22), (5, 2)])
            line([(15, 2), (15, 7), (20, 7)])
            line([(8, 12), (17, 12)])
            line([(8, 16), (17, 16)])
        else:
            raise ValueError(name)
        self.scene.els[first].setdefault('customData', {}).update(iconName=name)
        self.groups.pop(0)

    def action(self, key, x, y, w, title, glyph, rows, output, *, step=None, role=None, kind='function', eyebrow=None):
        """Scan-friendly card: icon/title band, labeled rows, distinct output strip."""
        if kind not in ('function', 'skill'):
            raise ValueError('Action kind must be function or skill')
        self.groups.insert(0, key)
        row_heights = [max(23, value.count('\n') * 23 + 23) + 12 for _, value in rows]
        footer_y = 90 + sum(row_heights)
        height = math.ceil(footer_y + 60 + 23 * output.count('\n'))
        shape = self.box(x, y, w, height, fill=self.SURFACE, stroke=self.ACCENT if kind == 'function' else self.TEXT, rounded=kind == 'skill')
        shape['strokeWidth'] = 2
        shape['customData'] = dict(nodeKind=kind, role=role or key, layout='labeled-rows')
        if step is not None:
            shape['customData']['step'] = step
        header = self.box(x + 1, y + 1, w - 2, 72, fill=self.TINT if kind == 'function' else self.TEXT, stroke='transparent', rounded=kind == 'skill')
        header['customData'] = dict(cardPart='header')
        if glyph:
            self.icon(glyph, x + 22, y + 20, 34, self.CANVAS if kind == 'skill' else self.ACCENT)
        title_x = x + (74 if glyph else 22)
        tag = eyebrow or (f'{step:02}  ·  ' if step is not None else '') + kind.upper()
        self.text(title_x, y + 12, tag, size=13, color=self.CANVAS if kind == 'skill' else self.SECONDARY)
        self.text(title_x, y + 33, title, size=26, color=self.CANVAS if kind == 'skill' else self.TEXT)
        row_y = y + 90
        for (label, value), row_h in zip(rows, row_heights):
            self.text(x + 22, row_y + 3, label.upper(), size=13, color=self.SECONDARY)
            self.text(x + 112, row_y, value, size=18)
            row_y += row_h
        self.rule(x + 22, y + footer_y, x + w - 22)
        self.text(x + 22, y + footer_y + 21, 'OUTPUT', size=13, color=self.SECONDARY)
        self.text(x + 112, y + footer_y + 17, output, size=18, color=self.ACCENT)
        self.groups.pop(0)
        return shape

    def embed_image(self, path, x, y, width, height, *, provider=None, source=None):
        path = Path(path)
        data = path.read_bytes()
        file_id = hashlib.sha1(data).hexdigest()
        mime = mimetypes.guess_type(path.name)[0]
        if not mime or not mime.startswith('image/'):
            raise ValueError(f'Not an image: {path}')
        self.image_files[file_id] = dict(id=file_id, mimeType=mime, created=0,
            dataURL=f'data:{mime};base64,'+base64.b64encode(data).decode())
        return self.add(self._base('image', x, y, width, height, fileId=file_id,
            status='saved', scale=[1,1], crop=None, strokeColor='transparent',
            customData=dict(provider=provider, source=source)))

    def doc(self, source='flowchart'):
        doc = self.scene.doc(source)
        doc['files'] = self.image_files
        doc['appState']['viewBackgroundColor'] = self.CANVAS
        return doc

    def write(self, path, *, name=None):
        doc = self.doc()
        if name:
            doc['appState']['name'] = name
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2)+'\n')
        return path
