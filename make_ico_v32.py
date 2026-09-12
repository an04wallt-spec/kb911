from pathlib import Path
import struct

SIZES = [256, 128, 64, 48, 40, 32, 24, 20, 16]
PNG_SIG = b'\x89PNG\r\n\x1a\n'

def build_ico(prefix: str, output: str) -> None:
    frames = []
    for size in SIZES:
        p = Path('build') / f'{prefix}_{size}.png'
        data = p.read_bytes()
        if not data.startswith(PNG_SIG):
            raise SystemExit(f'Not PNG: {p}')
        # Verify PNG IHDR dimensions exactly match the advertised ICO frame.
        width, height = struct.unpack('>II', data[16:24])
        if (width, height) != (size, size):
            raise SystemExit(f'Bad frame size {p}: {width}x{height}')
        frames.append(data)

    header = struct.pack('<HHH', 0, 1, len(frames))
    offset = 6 + 16 * len(frames)
    entries = []
    for size, data in zip(SIZES, frames):
        dim = 0 if size == 256 else size
        entries.append(struct.pack('<BBBBHHII', dim, dim, 0, 0, 1, 32, len(data), offset))
        offset += len(data)

    blob = header + b''.join(entries) + b''.join(frames)
    Path(output).write_bytes(blob)

    # Parse our own output again before it can be embedded into the EXE.
    out = Path(output).read_bytes()
    reserved, kind, count = struct.unpack_from('<HHH', out, 0)
    if (reserved, kind, count) != (0, 1, len(SIZES)):
        raise SystemExit(f'Invalid ICO header: {output}')
    got = []
    for i in range(count):
        w, h, colors, reserved2, planes, bpp, byte_count, image_offset = struct.unpack_from(
            '<BBBBHHII', out, 6 + 16 * i
        )
        size = 256 if w == 0 else w
        got.append(size)
        if (256 if h == 0 else h) != size or planes != 1 or bpp != 32:
            raise SystemExit(f'Invalid ICO entry {i}: {output}')
        frame = out[image_offset:image_offset + byte_count]
        if not frame.startswith(PNG_SIG):
            raise SystemExit(f'ICO frame {i} is not PNG: {output}')
    if got != SIZES:
        raise SystemExit(f'ICO sizes mismatch: {output}: {got}')

build_ico('kb911_app', r'build\KB911.ico')
build_ico('kb911_project', r'build\KB911_project.ico')
print('KB911 v32 ICO validation OK: 9 PNG-backed frames in each icon')
