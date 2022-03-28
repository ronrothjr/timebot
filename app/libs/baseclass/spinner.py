from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang.builder import Builder
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.widget import Widget
from kivymd.theming import ThemableBehavior


class AKSpinnerBase(ThemableBehavior, Widget):
    spinner_size = NumericProperty(48)
    speed = NumericProperty(0.4)
    active = BooleanProperty(False)
    color = ListProperty()


class AKSpinnerCircleFlip(AKSpinnerBase):
    animation = StringProperty("out_back")

    _circle_size = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _start_animate(self, size):
        size = [size, size]
        self.flip_v_start = Animation(
            _circle_size=[size[0], size[1]],
            opacity=1,
            duration=self.speed,
            t=self.animation,
        )
        self.flip_v = (
            Animation(
                _circle_size=[size[0], 0],
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _circle_size=[size[0], size[1]],
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _circle_size=[0, size[1]],
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _circle_size=[size[0], size[1]],
                duration=self.speed,
                t=self.animation,
            )
        )
        self.flip_v.repeat = True
        self.flip_v_start.start(self)
        Clock.schedule_once(lambda x: self.flip_v.start(self), self.speed)

    def _stop_animate(self):
        self.flip_v_start.cancel_all(self)
        self.flip_v.cancel_all(self)
        self.flip_v_stop = Animation(
            _circle_size=[0, 0], opacity=0, duration=0.1, t=self.animation
        )
        self.flip_v_stop.start(self)

    def on_active(self, *args):
        size = self.size[0]
        if self.active:
            self._start_animate(size)
        else:
            self._stop_animate()


class AKSpinnerDoubleBounce(AKSpinnerBase):
    color_secondary = ListProperty()

    _circle_size1 = ListProperty([0, 0])
    _circle_size2 = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _update(self, size):
        self._circle_size1 = [size, size]
        self._circle_size2 = [0, 0]
        self._start_animate(size)

    def _start_animate(self, size):
        self.anim0 = Animation(
            _circle_size1=[size, size],
            opacity=1,
            t="out_quad",
            duration=self.speed,
        )

        self.anim1 = Animation(
            _circle_size1=[size / 2, size / 2], t="in_quad", duration=self.speed
        ) + Animation(
            _circle_size1=[size, size], t="out_quad", duration=self.speed
        )

        self.anim2 = (
            Animation(
                _circle_size2=[size / 2, size / 2],
                opacity=1,
                t="in_quad",
                duration=self.speed,
            )
            + Animation(_circle_size2=[0, 0], t="out_quad", duration=self.speed)
        )
        self.anim1.repeat = True
        self.anim2.repeat = True

        self.anim0.start(self)
        Clock.schedule_once(lambda x: self.anim1.start(self), self.speed)
        Clock.schedule_once(lambda x: self.anim2.start(self), self.speed)

    def _stop_animate(self):
        self.anim0.cancel_all(self)
        self.anim1.cancel_all(self)
        self.anim2.cancel_all(self)
        self.anim1_stop = Animation(
            _circle_size1=[0, 0], opacity=0, t="in_quad", duration=0.1
        )
        self.anim2_stop = Animation(
            _circle_size2=[0, 0], opacity=0, t="in_quad", duration=0.1
        )
        self.anim1_stop.start(self)
        self.anim2_stop.start(self)

    def on_active(self, *args):
        size = self.size[0]
        if self.active:
            self._start_animate(size)
        else:
            self._stop_animate()


class AKSpinnerFoldingCube(AKSpinnerBase):
    angle = NumericProperty(45)
    animation = StringProperty("out_cubic")

    _cubeitem1 = ListProperty([0, 0])
    _cubeitem2 = ListProperty([0, 0])
    _cubeitem3 = ListProperty([0, 0])
    _cubeitem4 = ListProperty([0, 0])
    _cube1a = NumericProperty(0)
    _cube2a = NumericProperty(0)
    _cube3a = NumericProperty(0)
    _cube4a = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _start_animate(self, size):
        size /= 2
        self.cube_fold = (
            Animation(
                _cubeitem1=[size, size],
                _cube1a=1,
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _cubeitem2=[size, size],
                _cube2a=1,
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _cubeitem3=[size, size],
                _cube3a=1,
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _cubeitem4=[size, size],
                _cube4a=1,
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _cubeitem4=[0, size],
                _cube4a=0,
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _cubeitem3=[size, 0],
                _cube3a=0,
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _cubeitem2=[0, size],
                _cube2a=0,
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _cubeitem1=[size, 0],
                _cube1a=0,
                duration=self.speed,
                t=self.animation,
            )
        )
        self.cube_fold.repeat = True
        self.cube_fold.start(self)

    def _update(self, size):
        self._cubeitem1 = [size / 2, 0]
        self._cubeitem2 = [0, size / 2]
        self._cubeitem3 = [size / 2, 0]
        self._cubeitem4 = [0, size / 2]

    def _stop_animate(self, size):
        size /= 2
        self.cube_fold.cancel_all(self)
        self.cube_stop = (
            Animation(
                _cubeitem4=[0, size], _cube4a=0, duration=0.1, t=self.animation
            )
            + Animation(
                _cubeitem3=[size, 0], _cube3a=0, duration=0.1, t=self.animation
            )
            + Animation(
                _cubeitem2=[0, size], _cube2a=0, duration=0.1, t=self.animation
            )
            + Animation(
                _cubeitem1=[size, 0], _cube1a=0, duration=0.1, t=self.animation
            )
        )
        self.cube_stop.start(self)

    def on_active(self, *args):
        size = self.size[0]
        self._update(size)
        if self.active:
            self._start_animate(size)
        else:
            self._stop_animate(size)


class AKSpinnerThreeDots(AKSpinnerBase):

    animation = StringProperty("linear")

    _circle_size1 = ListProperty([0, 0])
    _circle_size2 = ListProperty([0, 0])
    _circle_size3 = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _start_animate(self, size):
        self.anim1 = (
            Animation(
                _circle_size1=[size, size],
                opacity=1,
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _circle_size1=[0, 0], duration=self.speed, t=self.animation
            )
            + Animation(duration=self.speed)
        )

        self.anim2 = (
            Animation(
                _circle_size2=[size, size],
                opacity=1,
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _circle_size2=[0, 0], duration=self.speed, t=self.animation
            )
            + Animation(duration=self.speed)
        )

        self.anim3 = (
            Animation(
                _circle_size3=[size, size],
                opacity=1,
                duration=self.speed,
                t=self.animation,
            )
            + Animation(
                _circle_size3=[0, 0], duration=self.speed, t=self.animation
            )
            + Animation(duration=self.speed)
        )

        self.anim1.repeat = True
        self.anim2.repeat = True
        self.anim3.repeat = True

        self.anim1.start(self)
        Clock.schedule_once(lambda dt: self.anim2.start(self), self.speed)
        Clock.schedule_once(lambda dt: self.anim3.start(self), self.speed * 2)

    def _stop_animate(self):
        self.anim1.cancel_all(self)
        self.anim2.cancel_all(self)
        self.anim3.cancel_all(self)
        self.anim1_stop = Animation(
            _circle_size1=[0, 0], opacity=0, duration=0.1, t=self.animation
        )
        self.anim2_stop = Animation(
            _circle_size2=[0, 0], opacity=0, duration=0.1, t=self.animation
        )
        self.anim3_stop = Animation(
            _circle_size3=[0, 0], opacity=0, duration=0.1, t=self.animation
        )
        self.anim1_stop.start(self)
        self.anim2_stop.start(self)
        self.anim3_stop.start(self)

    def on_active(self, *args):
        size = self.size[1]
        if self.active:
            self._start_animate(size)
        else:
            self._stop_animate()