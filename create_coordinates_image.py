import json
from PIL import Image, ImageDraw, ImageFont

# Load points from JSON file
with open("10_-19.json", "r") as f:
    data = json.load(f)
    points = data["points"]

# Load image
image = Image.open("img_1.png")
draw = ImageDraw.Draw(image)

# Draw points on the image
point_color = (255, 0, 0)  # Red color
text_color = (0, 0, 0)  # Black color
point_radius = 3
text_offset_x, text_offset_y = 5, 5

# Load default font, you can use custom font by replacing the line with:
# font = ImageFont.truetype("path/to/your/font.ttf", font_size)
font_size = 14
font = ImageFont.load_default()

for key, point in points.items():
    x, y = point
    draw.ellipse((x - point_radius, y - point_radius, x + point_radius, y + point_radius), fill=point_color)
    draw.text((x + text_offset_x, y + text_offset_y), key, font=font, fill=text_color)

# Save the image with points and their names
image.save("img_1_with_points_and_names.png")

# Display the image (optional)
image.show()
