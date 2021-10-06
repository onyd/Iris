from time import time

from kivy.clock import Clock
from kivy.config import Config
from kivy.metrics import sp
from functools import partial

from kivy.properties import OptionProperty, ObjectProperty, \
    BooleanProperty, NumericProperty, ReferenceListProperty, ColorProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Rectangle, Line, Color
from kivy.uix.behaviors import ButtonBehavior


class AntiCollisionObject:
    pass


class SelectDragBehavior(object):
    """This class is an adaptation of the DragBehavior class from kivy with selection feature"""
    drag_distance = NumericProperty(6)

    drag_rect_x = NumericProperty(0)
    drag_rect_y = NumericProperty(0)
    drag_rect_width = NumericProperty(100)
    drag_rect_height = NumericProperty(100)

    drag_rectangle = ReferenceListProperty(drag_rect_x, drag_rect_y,
                                           drag_rect_width, drag_rect_height)
    collision_margin = NumericProperty(3)
    selection_frame_color = ColorProperty((0., 0., 0., 1.))

    def __init__(self, **kwargs):
        self._drag_touch = None
        self.selected = False
        self.sdb_enabled = True

        super(SelectDragBehavior, self).__init__(**kwargs)

    def _get_uid(self, prefix='sv'):
        return '{0}.{1}'.format(prefix, self.uid)

    def select(self):
        self.selected = True
        self.draw_selection_box()

    def unselect(self):
        self.selected = False
        self.canvas.before.clear()
        self._drag_touch = None

    def draw_selection_box(self, margin=3):
        if not self.selected:
            return
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.selection_frame_color)
            Line(rectangle=(self.x - margin, self.y - margin,
                            self.width + 2 * margin, self.height + 2 * margin),
                 width=margin)

    def handle_collisions(self, dx=0, dy=0):
        new_dx, new_dy = dx, dy
        for child in self.parent.children:
            x, y = self.x + dx, self.y + dy

            # Collision test
            if child is not self and isinstance(
                    child, AntiCollisionObject) and (
                        x + self.width + self.collision_margin > child.x
                        and x - self.collision_margin < child.right
                        and y + self.height + self.collision_margin > child.y
                        and y - self.collision_margin < child.top):
                # Compute distance bl relatively to bottom left corner and tr the top right one
                bl_x = abs(x - child.x - child.width)
                bl_y = abs(y - child.y - child.height)
                tr_x = abs(child.x - x - self.width)
                tr_y = abs(child.y - y - self.height)

                d_min = min(bl_x, bl_y, tr_x, tr_y)
                if d_min == bl_x:
                    self.x = child.x + child.width + self.collision_margin
                    new_dx = 0
                elif d_min == bl_y:
                    self.y = child.y + child.height + self.collision_margin
                    new_dy = 0
                elif d_min == tr_x:
                    self.right = child.x - self.collision_margin
                    new_dx = 0
                else:
                    self.top = child.y - self.collision_margin
                    new_dy = 0

        return new_dx, new_dy

    def on_touch_down(self, touch):
        if not self.sdb_enabled:
            return super(SelectDragBehavior, self).on_touch_down(touch)

        xx, yy, w, h = self.drag_rectangle
        x, y = touch.pos

        if not self.collide_point(x, y):
            self.unselect()
            touch.ud[self._get_uid('svavoid')] = True
            return super(SelectDragBehavior, self).on_touch_down(touch)


        if self._drag_touch or ('button' in touch.profile and
                                touch.button.startswith('scroll')) or\
                not ((xx < x <= xx + w) and (yy < y <= yy + h)):
            return super(SelectDragBehavior, self).on_touch_down(touch)

        # no mouse scrolling and object is selected, so the user is going to drag with this touch.
        touch.grab(self)
        uid = self._get_uid()
        touch.ud[uid] = {'mode': 'unknown', 'dx': 0, 'dy': 0}

        # not selected so the user swipe to move in
        if not self.selected:
            return super(SelectDragBehavior, self).on_touch_down(touch)

        self._drag_touch = touch

        return True

    def on_touch_move(self, touch):
        # Avoid drag
        if not self.sdb_enabled:
            return super(SelectDragBehavior, self).on_touch_move(touch)

        if self._get_uid('svavoid') in touch.ud or\
                (self._drag_touch is not None and self._drag_touch is not touch)or not self.sdb_enabled:
            return super(SelectDragBehavior, self).on_touch_move(touch) or\
                self._get_uid() in touch.ud

        if touch.grab_current is not self:
            return True

        # Get touch mode
        uid = self._get_uid()
        ud = touch.ud[uid]
        mode = ud['mode']
        if mode == 'unknown':
            ud['dx'] += abs(touch.dx)
            ud['dy'] += abs(touch.dy)
            if ud['dx'] > sp(self.drag_distance) or ud['dy'] > sp(
                    self.drag_distance):
                mode = 'drag'
            ud['mode'] = mode

        # Drag
        if mode == 'drag' and self.selected:
            dx, dy = self.handle_collisions(touch.dx, touch.dy)
            self.x += dx
            self.y += dy

        self.draw_selection_box()
        return True

    def on_touch_up(self, touch):
        if not self.sdb_enabled:
            return super(SelectDragBehavior, self).on_touch_up(touch)

        x, y = touch.pos
        uid = self._get_uid()
        ud = touch.ud[uid]

        if self.collide_point(
                x, y) and not self.selected and ud['mode'] != 'drag':
            self.select()
            return True

        self.handle_collisions()
        self.draw_selection_box()

        # avoid the drag if touch doesn't correspond
        if self._get_uid('svavoid') in touch.ud:
            return super(SelectDragBehavior, self).on_touch_up(touch)

        if self._drag_touch and self in [x() for x in touch.grab_list]:
            touch.ungrab(self)
            self._drag_touch = None
            ud = touch.ud[self._get_uid()]
            if ud['mode'] == 'unknown':
                super(SelectDragBehavior, self).on_touch_down(touch)
                Clock.schedule_once(partial(self._do_touch_up, touch), .1)
        else:
            if self._drag_touch is not touch:
                super(SelectDragBehavior, self).on_touch_up(touch)

        return self._get_uid() in touch.ud

    def _do_touch_up(self, touch, *largs):
        super(SelectDragBehavior, self).on_touch_up(touch)
        # don't forget about grab event!
        for x in touch.grab_list[:]:
            touch.grab_list.remove(x)
            x = x()
            if not x:
                continue
            touch.grab_current = x
            super(SelectDragBehavior, self).on_touch_up(touch)
        touch.grab_current = None


class UndispatchBehavior(object):
    def on_touch_down(self, touch):
        return

    def on_touch_move(self, touch):
        return

    def on_touch_up(self, touch):
        return


class UndispatchButtonBehavior(ButtonBehavior):
    '''
    This class is an adaptation of ButtonBehavior which doesn't dispatch touch events to children

    '''
    def on_touch_down(self, touch):
        # if super(ButtonBehavior, self).on_touch_down(touch):
        #     return True
        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False
        if self in touch.ud:
            return False
        touch.grab(self)
        touch.ud[self] = True
        self.last_touch = touch
        self.__touch_time = time()
        self._do_press()
        self.dispatch('on_press')
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            return True
        # if super(ButtonBehavior, self).on_touch_move(touch):
        #     return True
        return self in touch.ud

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return  #super(ButtonBehavior, self).on_touch_up(touch)
        assert (self in touch.ud)
        touch.ungrab(self)
        self.last_touch = touch

        if (not self.always_release and not self.collide_point(*touch.pos)):
            self._do_release()
            return

        touchtime = time() - self.__touch_time
        if touchtime < self.min_state_time:
            self.__state_event = Clock.schedule_once(
                self._do_release, self.min_state_time - touchtime)
        else:
            self._do_release()
        self.dispatch('on_release')
        return True
