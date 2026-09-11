import os
from PIL import Image

FLAG = os.environ.get("FLAG", "flag{phantom_stego_recovered_missing}")


def embed_lsb(path: str, message: str) -> None:
    img = Image.new("RGB", (256, 256), color=(20, 24, 32))
    pixels = img.load()
    bits = "".join(f"{ord(c):08b}" for c in message) + "00000000"

    idx = 0
    for y in range(img.height):
        for x in range(img.width):
            if idx >= len(bits):
                break
            r, g, b = pixels[x, y]
            r = (r & ~1) | int(bits[idx])
            pixels[x, y] = (r, g, b)
            idx += 1
        if idx >= len(bits):
            break

    img.save(path)


if __name__ == "__main__":
    embed_lsb("/app/static/transmission.png", FLAG)
