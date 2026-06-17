from PIL import Image
import os

# 读取图标合集
img = Image.open(r'C:\Users\谭\PycharmProjects\PythonProject2\images\图标.png')
width, height = img.size
print(f"原图尺寸: {width}x{height}")

# 6列3行
cols, rows = 6, 3
cell_w = width / cols
cell_h = height / rows
print(f"每格: {cell_w:.0f}x{cell_h:.0f}")

# 图标名称（按行列顺序）
icon_names = [
    ["典籍", "毛笔", "砚台", "纸张", "墨锭", "灯笼"],
    ["竹简", "书案", "印章", "卷轴", "线装书", "云纹"],
    ["窗棂", "竹影", "亭台", "山水", "桥梁", "梅花"]
]

# 创建输出目录
output_dir = 'images/icons'
os.makedirs(output_dir, exist_ok=True)

# 裁切每个图标
for row in range(rows):
    for col in range(cols):
        name = icon_names[row][col]
        x = int(col * cell_w)
        y = int(row * cell_h)
        w = int(cell_w)
        h = int(cell_h)

        # 裁切
        icon = img.crop((x, y, x + w, y + h))

        # 保存
        filepath = os.path.join(output_dir, f"{name}.png")
        icon.save(filepath, 'PNG')
        print(f"✓ {name}.png ({w}x{h})")

print(f"\n完成！共 {cols * rows} 个图标保存到: {output_dir}")
