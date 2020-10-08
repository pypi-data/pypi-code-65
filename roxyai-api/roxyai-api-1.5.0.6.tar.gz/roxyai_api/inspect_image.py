# (c) Roxy Corp. 2020-
# Roxy AI Coordinator
from __future__ import annotations
from typing import Optional
from enum import IntEnum
import numpy as np
import struct
import cv2
import traceback
from pathlib import Path

import logging.config
log = logging.getLogger(__name__)


class ImageFormat(IntEnum):
    RAW = 0x01
    JPEG = 0x02
    PNG = 0x03
    BMP = 0x04
    NDARRAY = 0xFF


IMG_FORMAT_RAW = ImageFormat.RAW
IMG_FORMAT_JPEG = ImageFormat.JPEG
IMG_FORMAT_PNG = ImageFormat.PNG
IMG_FORMAT_BMP = ImageFormat.BMP
IMG_FORMAT_NDARRAY = ImageFormat.NDARRAY

IMG_FORMAT_SUF = {
    ImageFormat.RAW: '.bin',
    ImageFormat.JPEG: '.jpg',
    ImageFormat.PNG: '.png',
    ImageFormat.BMP: '.bmp',
    ImageFormat.NDARRAY: '.ndarray',
}

IMG_SUFFIX_FMT = {v: k for k, v in IMG_FORMAT_SUF.items()}


def _bin_to_ndarary(src):
    # 構造情報の設定
    width, height, colors = struct.unpack('< H H B', src[:5])
    dt = np.dtype('uint8')
    dt = dt.newbyteorder('<')
    dst = np.frombuffer(src, dtype=dt, offset=5)
    if colors == 1:
        dst = dst.reshape((height, width))
        dst = cv2.cvtColor(dst, cv2.COLOR_GRAY2RGB)
    elif colors == 4:
        dst = dst.reshape((height, width, colors))
        dst = cv2.cvtColor(dst, cv2.COLOR_BGRA2RGB)
    else:
        dst = dst.reshape((height, width, colors))
    return dst


def _image_to_ndarary(src):
    dt = np.dtype('uint8')
    dt = dt.newbyteorder('<')
    buf = np.frombuffer(src, dtype=dt, offset=0)
    buf = cv2.imdecode(buf, cv2.IMREAD_IGNORE_ORIENTATION | cv2.IMREAD_COLOR)
    dst = cv2.cvtColor(buf, cv2.COLOR_BGR2RGB)
    return dst


def _ndarary_to_bin(src) -> bytes:
    shape = src.shape
    if len(shape) == 2:
        # グレースケールの場合は色数情報を追加
        shape = (*shape, 1)
    dst = struct.pack('< H H B', *shape)
    dst += src.tobytes()
    return dst


def _ndarary_to_jpeg(src) -> bytes:
    buf = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
    params = (cv2.IMWRITE_JPEG_QUALITY, 95)
    ret, dst = cv2.imencode('.jpg', buf, params=params)
    if not ret:
        RuntimeWarning('imencode for jpg failed')
    return bytes(np.frombuffer(dst, dtype=np.uint8))


def _ndarary_to_png(src) -> bytes:
    buf = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
    params = (cv2.IMWRITE_PNG_COMPRESSION, 1)
    ret, dst = cv2.imencode('.png', buf, params=params)
    if not ret:
        RuntimeWarning('imencode for png failed')
    return bytes(np.frombuffer(dst, dtype=np.uint8))


def _ndarary_to_bmp(src) -> bytes:
    buf = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
    ret, dst = cv2.imencode('.bmp', buf)
    if not ret:
        RuntimeWarning('imencode for bmp failed')
    return bytes(np.frombuffer(dst, dtype=np.uint8))


class InspectImage():
    """ 検査に利用するイメージデータのキャッシュ機能付き管理クラス
    """
    DECODER = {
        ImageFormat.RAW: _bin_to_ndarary,
        ImageFormat.JPEG: _image_to_ndarary,
        ImageFormat.PNG: _image_to_ndarary,
        ImageFormat.BMP: _image_to_ndarary,
    }

    ENCODER = {
        ImageFormat.RAW: _ndarary_to_bin,
        ImageFormat.JPEG: _ndarary_to_jpeg,
        ImageFormat.PNG: _ndarary_to_png,
        ImageFormat.BMP: _ndarary_to_bmp,
    }

    def __init__(
        self,
        fmt: ImageFormat,
        data: bytes,
        path: Optional[Path] = None,
        parent: Optional[InspectImage] = None,
        zoom: Optional[float] = 1.0,
        fnc_buf_release: Optional[callable] = None,
    ):
        self._org_fmt = fmt
        self._data = {fmt: data}
        self._fnc_buf_release = fnc_buf_release
        self._path = path
        self._parent = parent
        self._zoom = zoom
        self._keep_count = 1
        # if fmt != ImageFormat.NDARRAY:
        #     # 基準となる ndarray データを作成する
        #     self.__convert()

    @classmethod
    def load(cls, path) -> InspectImage:
        """ ファイルから画像を読み込む
        """
        instance = None
        imgfile = Path(path)
        if imgfile.exists():
            fmt = IMG_SUFFIX_FMT.get(imgfile.suffix)
            if fmt:
                data = imgfile.read_bytes()
                instance = cls(fmt, data, imgfile)
        return instance

    def save(self, path) -> bool:
        """ ファイルに画像を書き込む
        Returns:
            True:   書き込み成功
            False:  書き込み失敗
        Note:
            ファイル名の拡張子で画像フォーマットを決定する
        """
        imgfile = Path(path)
        fmt = IMG_SUFFIX_FMT.get(imgfile.suffix)
        if fmt:
            data = self.get_image(fmt)
            if data:
                imgfile.write_bytes(data)
                return True
        return False

    def get_image(self, fmt: ImageFormat = ImageFormat.NDARRAY) -> Optional[np.ndarray, bytes]:
        """ 指定フォーマトの画像データを取得
        """
        img = self._data.get(fmt)
        if img is not None:
            # 対象フォーマットがキャッシュにあればそれを返す
            return img
        # 無ければ画像変換してそれを返す
        self.__convert(fmt)
        img = self._data.get(fmt)
        return img

    def get_size(self, fmt: ImageFormat = None) -> int:
        """ 指定フォーマットのデータサイズを取得
        """
        fmt = fmt or self._org_fmt
        img = self.get_image(fmt)
        if img is None:
            return None
        if fmt == ImageFormat.NDARRAY:
            return img.size
        else:
            return len(img)

    def __convert(self, fmt: ImageFormat = ImageFormat.NDARRAY):
        """ 画像フォーマット変換
        """
        if self._data.get(fmt) is not None:
            # 変換済みなら何もしない
            return

        if self._data.get(ImageFormat.NDARRAY) is None:
            # 基準データ(ndarray)の作成
            src = self._data[self._org_fmt]
            converter = self.DECODER[self._org_fmt]
            try:
                dst = converter(src)
            except Exception as e:
                log.warning(traceback.format_exc())
                raise ImageConvertionFailed(self._org_fmt, ImageFormat.NDARRAY, e)
            self._data[ImageFormat.NDARRAY] = dst

        if fmt != ImageFormat.NDARRAY:
            # 基準データ(ndarray)から変換先の画像データの作成
            src = self._data[ImageFormat.NDARRAY]
            converter = self.ENCODER[fmt]
            try:
                dst = converter(src)
            except Exception as e:
                log.warning(traceback.format_exc())
                raise ImageConvertionFailed(ImageFormat.NDARRAY, fmt, e)
            self._data[fmt] = dst

    def keep(self):
        """ 画像データを保持する
        """
        self._keep_count += 1

    def release(self):
        """ 画像データを全て破棄する
        """
        self._keep_count -= 1
        if self._keep_count > 0:
            # まだ保持している処理があるので破棄しない
            return
        self._data.clear()
        self._org_fmt = None
        if self._fnc_buf_release:
            # バッファの解放コールバックの呼び出し
            try:
                self._fnc_buf_release()
            except Exception as e:
                log.warning(
                    f"{e}: in callback for release image buffer: "
                    f"{self._fnc_buf_release()}"
                )
            self._fnc_buf_release = None

    def __str__(self):
        string = (
            f'org_image[{IMG_FORMAT_SUF.get(self._org_fmt)}], '
            'cached '
        )
        cached = [
            f'{name}: {len(self._data.get(fmt)):,d} bytes'
            for fmt, name in IMG_FORMAT_SUF.items()
            if type(self._data.get(fmt)) is bytes
        ]
        raw = self._data.get(ImageFormat.NDARRAY)
        if type(raw) is np.ndarray:
            cached.append(
                f'{IMG_FORMAT_SUF[ImageFormat.NDARRAY]}: '
                f'{raw.size:,d} bytes'
            )
        string += ', '.join(cached)
        return string

    # 読み取り専用のパラメータアクセス定義
    @property
    def format(self) -> int:
        return self._org_fmt

    @property
    def data(self) -> int:
        return self._data

    @property
    def path(self) -> Path:
        return self._path

    @property
    def parent(self) -> InspectImage:
        return self._parent

    @property
    def zoom(self) -> float:
        return self._zoom


class ImageConvertionFailed(RuntimeWarning):
    """ 画像変換エラー
    """
    def __init__(self, src_fmt, dst_fmt, exception):
        self.src_fmt = src_fmt
        self.dst_fmt = dst_fmt
        self.exception = exception

    def __str__(self):
        return (
            f'image conversion failed '
            f'from [{IMG_FORMAT_SUF.get(self.src_fmt)}] '
            f'to [{IMG_FORMAT_SUF.get(self.dst_fmt)}] '
        )
