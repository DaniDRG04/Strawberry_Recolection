# image_to_bits.py

def image_to_bits(image_path: str):
    # Read file in binary mode
    with open(image_path, "rb") as f:
        data = f.read()

    # Convert to a list of byte values (0–255)
    return list(data)

if __name__ == "__main__":
    # Example: replace with your image path
    img_path = r"src\assets\icon\Temp.png"

    bits = image_to_bits(img_path)

    # Print as a JS-friendly Uint8Array
    print("const testBits = new Uint8Array([")
    for i, b in enumerate(bits):
        end = ", " if i < len(bits) - 1 else ""
        print(b, end=end)
        if (i + 1) % 16 == 0:  # line break every 16 numbers
            print()
    print("]);")
