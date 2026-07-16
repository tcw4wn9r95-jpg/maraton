"""Minimal FIT file encoder for workout files.

Generates binary .fit files compatible with TrainingPeaks, Garmin, and other
platforms that support the ANT+ FIT protocol workout file type.
"""

import struct
import datetime

FIT_HEADER_SIZE = 14
PROTOCOL_VERSION = 0x20  # 2.0
PROFILE_VERSION = 2132   # 21.32

# FIT base types
ENUM = 0x00
UINT8 = 0x0D
UINT16 = 0x84
UINT32 = 0x86
SINT32 = 0x85
STRING = 0x07

# Message numbers
MESG_FILE_ID = 0
MESG_WORKOUT = 26
MESG_WORKOUT_STEP = 27

# File type
FILE_WORKOUT = 5

# Workout step duration types
DURATION_TIME = 0
DURATION_DISTANCE = 1
DURATION_OPEN = 5
DURATION_REPEAT_UNTIL_STEPS_COMPLETE = 6

# Workout step target types
TARGET_SPEED = 0
TARGET_HEART_RATE = 1
TARGET_OPEN = 2
TARGET_CADENCE = 3

# Workout step intensity
INTENSITY_ACTIVE = 0
INTENSITY_REST = 1
INTENSITY_WARMUP = 2
INTENSITY_COOLDOWN = 3

# Sport
SPORT_RUNNING = 1
SUB_SPORT_GENERIC = 0

CRC_TABLE = [
    0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
    0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
]


def fit_crc(data: bytes) -> int:
    crc = 0
    for byte in data:
        tmp = CRC_TABLE[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ CRC_TABLE[byte & 0xF]
        tmp = CRC_TABLE[crc & 0xF]
        crc = (crc >> 4) & 0x0FFF
        crc = crc ^ tmp ^ CRC_TABLE[(byte >> 4) & 0xF]
    return crc


def _encode_field(value, base_type):
    if base_type == ENUM or base_type == UINT8:
        return struct.pack("<B", value)
    elif base_type == UINT16:
        return struct.pack("<H", value)
    elif base_type == UINT32:
        return struct.pack("<I", value)
    elif base_type == SINT32:
        return struct.pack("<i", value)
    elif base_type == STRING:
        encoded = value.encode("utf-8") if isinstance(value, str) else value
        return encoded
    return b""


def _base_type_size(base_type):
    if base_type in (ENUM, UINT8):
        return 1
    elif base_type in (UINT16,):
        return 2
    elif base_type in (UINT32, SINT32):
        return 4
    return 0


class FitEncoder:
    def __init__(self):
        self._records = bytearray()
        self._local_mesg_types = {}
        self._next_local = 0

    def _define_mesg(self, global_mesg_num, fields):
        local = self._next_local
        self._next_local += 1
        self._local_mesg_types[global_mesg_num] = local

        record = bytearray()
        record.append(0x40 | local)  # definition record header
        record.append(0)  # reserved
        record.append(0)  # little-endian
        record.extend(struct.pack("<H", global_mesg_num))
        record.append(len(fields))

        for field_num, size, base_type in fields:
            record.append(field_num)
            record.append(size)
            record.append(base_type)

        self._records.extend(record)

    def _data_mesg(self, global_mesg_num, data: bytes):
        local = self._local_mesg_types[global_mesg_num]
        self._records.append(local)  # data record header
        self._records.extend(data)

    def add_file_id(self, serial_number=12345):
        garmin_epoch = datetime.datetime(1989, 12, 31, tzinfo=datetime.timezone.utc)
        now = datetime.datetime.now(datetime.timezone.utc)
        timestamp = int((now - garmin_epoch).total_seconds())

        fields = [
            (0, 1, ENUM),    # type
            (1, 2, UINT16),  # manufacturer
            (2, 2, UINT16),  # product
            (3, 4, UINT32),  # serial_number
            (4, 4, UINT32),  # time_created
        ]
        self._define_mesg(MESG_FILE_ID, fields)

        data = bytearray()
        data.extend(_encode_field(FILE_WORKOUT, ENUM))
        data.extend(_encode_field(1, UINT16))  # manufacturer: Garmin
        data.extend(_encode_field(0, UINT16))  # product
        data.extend(_encode_field(serial_number, UINT32))
        data.extend(_encode_field(timestamp, UINT32))
        self._data_mesg(MESG_FILE_ID, data)

    def add_workout(self, name: str, num_steps: int, sport=SPORT_RUNNING):
        name_bytes = name.encode("utf-8")[:40]
        name_bytes = name_bytes + b"\x00" * (41 - len(name_bytes))
        name_size = 41

        fields = [
            (4, 1, ENUM),           # sport
            (5, 1, ENUM),           # sub_sport
            (6, 2, UINT16),         # num_valid_steps
            (8, name_size, STRING), # wkt_name
        ]
        self._define_mesg(MESG_WORKOUT, fields)

        data = bytearray()
        data.extend(_encode_field(sport, ENUM))
        data.extend(_encode_field(SUB_SPORT_GENERIC, ENUM))
        data.extend(_encode_field(num_steps, UINT16))
        data.extend(name_bytes)
        self._data_mesg(MESG_WORKOUT, data)

    def add_workout_step(self, message_index, duration_type, duration_value,
                         target_type, target_value, target_low, target_high,
                         intensity, notes=""):
        notes_bytes = notes.encode("utf-8")[:100]
        notes_bytes = notes_bytes + b"\x00" * (101 - len(notes_bytes))
        notes_size = 101

        if message_index == 0:
            fields = [
                (254, 2, UINT16),          # message_index
                (0, 4, UINT32),            # duration_value
                (1, 4, UINT32),            # target_value
                (2, 4, UINT32),            # custom_target_value_low
                (3, 4, UINT32),            # custom_target_value_high
                (4, 1, ENUM),              # duration_type
                (5, 1, ENUM),              # target_type
                (6, 1, ENUM),              # intensity
                (7, notes_size, STRING),   # notes
            ]
            self._define_mesg(MESG_WORKOUT_STEP, fields)

        data = bytearray()
        data.extend(_encode_field(message_index, UINT16))
        data.extend(_encode_field(duration_value, UINT32))
        data.extend(_encode_field(target_value, UINT32))
        data.extend(_encode_field(target_low, UINT32))
        data.extend(_encode_field(target_high, UINT32))
        data.extend(_encode_field(duration_type, ENUM))
        data.extend(_encode_field(target_type, ENUM))
        data.extend(_encode_field(intensity, ENUM))
        data.extend(notes_bytes)
        self._data_mesg(MESG_WORKOUT_STEP, data)

    def build(self) -> bytes:
        data_bytes = bytes(self._records)
        data_size = len(data_bytes)

        header = struct.pack(
            "<BBHI4s",
            FIT_HEADER_SIZE,
            PROTOCOL_VERSION,
            PROFILE_VERSION,
            data_size,
            b".FIT",
        )
        header_crc = fit_crc(header)
        header = header + struct.pack("<H", header_crc)

        full = header + data_bytes
        data_crc = fit_crc(full)
        return full + struct.pack("<H", data_crc)
