'''
1. Chương trình mô phỏng một amr hoạt động với các chức năng chính sau:
    - Hoạt động dựa trên bản đồ được xây dựng trước
    - Tránh vật cản tĩnh và tường trên bản đồ
2. Mô tả chuyển động của 01 amr:
    - Mỗi chu kỳ chuyển động: tìm kiếm tập hợp hướng đi -> chọn hướng đi phù hợp với tập hợp các yêu cầu -> tiến một bước -> quay lại chọn hướng đi
    - Tại một chu kỳ chuyển động amr có thể quay 1 trong 4 hướng (90/đi lên, 180/trái, 0/phải, 270/xuống dưới) ứng với hệ toạ độ oxy
    - Trong một chu kỳ chuyển động amr dịch chuyển một đoạn step theo 1 trong 2 trục x hoặc y
4. Thiết kế chương trình:
4.1. Ý tưởng: 
Mô phỏng hoạt động của một amr trên cùng một bản đồ trong không gian 2D. Thế giới thực là: bản đồ 2D và xe amr theo lập trình thủ tục.
Xe amr là một hệ thống Cơ điện tử gồm:
- Phần cứng: bộ não (máy tính) + cơ cấu chuyển động (xe + bánh).
- Phần mềm: Chương trình phần mềm trong bộ não (máy tính) để điều khiển xe hoạt động.
4.2. Cơ sở dữ liệu:
- Bản đồ thực: hệ tọa độ 2D, vật cản tĩnh tại các tọa độ 2D (tường là trường hợp đặc biệt của vật cản tĩnh và là kích thước của bản đồ).
- Bản đồ ảo trong bộ não (máy tính): Bản đồ ảo được biểu diễn bằng ma trận có các phần tử ứng với các vị trí trên bản đồ thật.
- Các phương thức của bản đồ và chuyển đổi giữa hai bản đồ.
- Cơ sở dữ liệu về amr: thuộc tính và phương thức.
- Tập hợp vị trí và hướng tức thời của amr trên bản đồ ảo.
'''
import turtle
from random import *
import serial
import time


#Xay dung kien thuc ve ban do
#Hàm khởi tạo bản đồ
def map_init(node_row, node_column):
    map = []
    for row in range(node_row):
            new_row = []
            for col in range(node_column):
                if (row == 0)|(row == node_row - 1)|(col == 0)|(col == node_column - 1):
                    new_node = 1
                else:
                    new_node = 0
                new_row.append(new_node)
            map.append(new_row)
    send_command("map= "+str(node_row)+"x"+str(node_column))
    return map
#Hàm in bản đồ ra terminal (text)
def print_map(map):
    for row in range(len(map)):
        for col in range(len(map[row])):
            print(f' {map[row][col]} ', end='')
        print(f'\n')     
#Hàm vẽ bản đồ trên màn hình turtle (pixel)
def draw_map(map, color, pen, width_half, height_half):
    pen.color(color)
    pen.speed(0)
    for row in range(len(map)):
        pen.seth(0)
        pen.up( )
        pen.goto(turn2pixel(map, height_half, width_half, row, 0))
        pen.down()
        pen.write(row,align='left',font=('Arial', 8, 'normal'))
        pen.goto(turn2pixel(map, height_half, width_half, row, len(map[row]) - 1))
    for col in range(len(map[0])):
        pen.seth(-90)
        pen.up()
        pen.goto(turn2pixel(map, height_half, width_half, 0, col))
        pen.down()
        pen.write(col,font=('Arial', 8, 'normal'))
        pen.goto(turn2pixel(map, height_half, width_half, len(map) - 1, col))
    for row in range(len(map)):
        for col in range(len(map[row])):
            if map[row][col] != 0:
                pen.up()
                pen.goto(turn2pixel(map, height_half, width_half, row, col))
                pen.down()
                pen.dot(5, "red")
                send_command("obs= "+str(row)+'x'+str(col))
#Hàm chuyển vị trí phần tử trên bản đồ ma trận thành tọa độ pixel trên bản đồ turtle
def turn2pixel(map, height_half, width_half, row_position, col_position):
    row_segment = len(map) - 1
    col_segment = len(map[0]) - 1
    row_distance = 2 * height_half/row_segment
    col_distance = 2 * width_half/col_segment
    x_pixel = -width_half + col_position * col_distance
    y_pixel = height_half - row_position * row_distance
    return [x_pixel, y_pixel]
#Hàm chuyển vị trí amr trên bản đồ turtle sang vị trí phần tử trên bản đồ ma trận
def turn2node(map, width_half, height_half, x_pixel, y_pixel):
    row_segment = len(map) - 1
    col_segment = len(map[0]) - 1
    row_distance = 2 * height_half/row_segment
    col_distance = 2 * width_half/col_segment
    row_pos = round((height_half - y_pixel)/row_distance)
    col_pos = round((x_pixel + width_half)/col_distance)
    return [row_pos, col_pos]
#Hàm tạo ngẫu nhiên vật cản trên bản đồ ma trận
def map_random(map):
    for row in range(1, len(map) - 1):
        for col in range(1, len(map[row]) - 1):
            obstacle = choice((0, 0, 0, 0, 1 , 1, 0, 0, 0, 0, 0, 0, 0))
            map[row][col] = obstacle   
#Hàm tìm kiếm khả năng chuyển động tiếp theo theo 4 hướng của amr
def nextorient_set(map, row_node, col_node):
    set_result = []
    if (map[row_node - 1][col_node] == 0):
        set_result.append(90)
    if (map[row_node + 1][col_node] == 0):
        set_result.append(270)
    if (map[row_node][col_node -1] == 0):
        set_result.append(180)
    if (map[row_node][col_node + 1] == 0):
        set_result.append(0)
    return set_result
#Hàm kiểm tra vị trí hiện tại có phải là tường không trên bản đồ ma trận
def is_wall(map, current_mposition):
    return (current_mposition[0] == 0) or (current_mposition[0] == len(map) - 1) or (current_mposition[1] == 0) or (current_mposition[1] == len(map[0]) - 1)

#Cơ sở kiến thức về amr
#Vẽ amr trên bản đồ turtle
def draw_amr(map, amr, width_half, height_half, current_ppos):
    amr.up()
    amr.goto(current_ppos)
    current_mpos = map.turn2node(map, width_half=width_half, height_half=height_half, x_pixel=current_ppos[0], y_pixel=current_ppos[1])
    return current_mpos
#Hàm tính toán chuyển động tiếp theo cho amr trong một chu kỳ
def run_rule(amr, mmap):
    global current_mpos
    current_mposition = current_mpos[:]
    send_command("x= "+str(current_mposition[0]))
    send_command("y= "+str(current_mposition[1]))
    if not is_wall(mmap, current_mposition):
        posible_set = nextorient_set(mmap, current_mposition[0], current_mposition[1])
        if (posible_set != []):
            amr.down()
            amr.seth(choice(posible_set))
            if amr.heading() == 90:
                current_mposition[0] -= 1
            elif amr.heading() == 270:
                current_mposition[0] += 1     
            elif amr.heading() == 180:
                current_mposition[1] -= 1
            elif amr.heading() == 0:
                current_mposition[1] += 1 
            current_mpos = current_mposition[:]
            send_command("dir= "+str(int(amr.heading())))
            

#Hàm vòng lặp các chu kỳ chuyển động của amr
def run(amr, mmap, width_half, height_half):
    global current_mpos
    amr.speed(1)
    amr.color('grey')
    is_OK = True
    while is_OK:
        run_rule(amr, mmap)
        current_ppos = turn2pixel(mmap, height_half, width_half, current_mpos[0], current_mpos[1])
        amr.up()
        amr.goto(current_ppos[0], current_ppos[1])
        


#btl bắt đầu từ đây
SERIAL_PORT = 'COM4'      
BAUDRATE = 115200
def send_command(command):
    with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as ser:
        # Send command followed by newline
        ser.write((command + '\n').encode())

        # Read response from esp (for debugging)
        #time.sleep(0.01)
        #response = ser.read_all().decode().strip()
        #print("Response from device:\n", response)


if __name__ == '__main__':
    turtle.mode("world")
    turtle.setworldcoordinates(-410, -710, 410, 710)
    turtle.setup(0.5, 0.5, 100, 100)
    turtle.Screen().bgcolor('black')
    window = turtle.Screen()
    mmap = map_init(6, 6)
    map_random(mmap)
    current_mpos = [3, 2]
    one_amr = turtle.Turtle('turtle')
    draw_map(mmap, 'blue', one_amr, 400, 700)
    run(one_amr, mmap, 400, 700)
window.exitonclick()