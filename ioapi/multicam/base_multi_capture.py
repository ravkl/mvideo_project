from ioapi.utils import PropertyHacker
from ioapi.multicam import Frame
from frozendict import frozendict
from datetime import *
from typing import *

# Фикс для версий питона < 3.7 (метод datetime.fromisoformat)
from backports.datetime_fromisoformat import MonkeyPatch
MonkeyPatch.patch_fromisoformat()


class BaseMultiCapture(metaclass=PropertyHacker):
    """
    Абстрактный базовый класс для мультиканального доступа к данным
    -------------------------------------------------------------
    Объявляет 4 публичных read-write атрибута:
    - pos (datetime or None) - текущая позиция воспроизведения
    - end (datetime or None) - конечная позиция воспроизведения
    - fpsx (int) - множитель FPS (см. ioapi.input.SeamlessCapture)
    - channels (tuple) - номера захватываемых каналов (int)
    """

    def __init__(self):
        self._pos = None
        self._end = None
        self._fpsx = 1
        self._channels = tuple()

    def read(self) -> Tuple[bool, Tuple[Frame]]:
        """
        Главный метод для синхронизированного чтения кадров
        из нескольких каналов. Аналогичен методу cv2.VideoCapture.read,
        но в качестве второго значения возвращает кортеж из нескольких
        кадров (объектов Frame).
        """
        raise NotImplementedError

    # Текущая позиция воспроизведения (pos)
    # -------------------------------------
    # При установке перематывает все каналы к указанному времени.
    # Обновляется при каждом считывании кадров методом read.
    # По умолчанию - None, поэтому должна быть задана желаемым
    # datetime объектом *до* первого вызова метода read.
    # При попытке вызова read без установки начальной позиции - исключение.

    def get_pos(self) -> Optional[datetime]:
        return self._pos
    def set_pos(self, pos: datetime):
        self._pos = pos
    pos = property(get_pos, set_pos, doc='Текущая позиция воспроизведения')

    # Конечная позиция воспроизведения (end)
    # --------------------------------------
    # Временная метка, после которой чтение новых кадров прекратится.
    # Прекращение чтения означает, что метод read возвращает пару False, None.
    # По умолчанию - None (без ограничения).

    def get_end(self) -> Optional[datetime]:
        return self._end
    def set_end(self, end: Optional[datetime]):
        self._end = end
    end = property(get_end, set_end, doc='Конечная позиция воспроизведения')

    # Множитель FPS (fpsx)
    # --------------------
    # Целое число > 0, задающее дискретизацию исходного FPS.
    # fpsx = 1 - возвращаются все кадры (по умолчанию)
    # fpsx = 2 - возвращается каждый второй кадр
    # fpsx = n - возвращается каждый n-ый кадр

    def get_fpsx(self) -> int:
        return self._fpsx
    def set_fpsx(self, fpsx: int):
        self._fpsx = fpsx
    fpsx = property(get_fpsx, set_fpsx, doc='Множитель FPS')

    # Номера захватываемых каналов (channels)
    # ---------------------------------------
    # Можно задать любой удобной итерируемой последовательностью интов.
    # Присутствует удаление дубликатов и сортировка. Также как и pos,
    # должно быть задано *до* первого вызова read, иначе - исключение.

    def get_channels(self) -> Tuple[int]:
        return self._channels
    def set_channels(self, channels: Iterable[int]):
        self._channels = tuple(sorted(set(channels)))
    channels = property(get_channels, set_channels, doc='Захватываемые каналы')