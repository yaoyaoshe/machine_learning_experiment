import numpy as np

#基地类
class Base:
    def __init__(self,x,y,fuel,missile,defense,value):
        #坐标
        self.x = x
        self.y = y
        #初始燃油量
        self.fuel = fuel
        #初始导弹数
        self.missile =missile
        #初始防御值
        self.defense =defense
        #军事价值
        self.value = value
    # 加油
    def refuel_for_plane(self,fuel_count):
        self.fuel -= fuel_count
    # 补充导弹
    def reload_missile(self,missile_count):
        self.missile -= missile_count
    # 遭受攻击
    def suffer_attack(self):
        self.defense -= 1

#蓝方基地
class BlueBase(Base):
     def __init__(self, x, y, fuel, missile, defense, value):
        super().__init__(x, y, fuel, missile, defense, value)
        self.factions=0

#红方基地
class RedBase(Base):
    def __init__(self, x, y, fuel, missile, defense, value):
        super().__init__(x, y, fuel, missile, defense, value)
        self.factions=1

    def suffer_attack(self):
        super().suffer_attack()
        if self.defense <= 0 :
            return self.value
        return -1

#飞机
class Plane:

    def __init__(self, id, x, y, fuel_capacity,missile_capacity):
        self.id=id
        self.x=x
        self.y=y
        self.fuel_capacity=fuel_capacity
        self.fuel = 0
        self.missile_capacity=missile_capacity
        self.missile = 0
        
    #上下左右 1234
    def move(self,direction):
        if(direction == 1):
            #向上方移动
            self.x -= 1
        elif(direction == 2):
            #向下方移动
            self.x += 1
        elif(direction == 3):
            #向左移动
            self.y -= 1
        elif(direction == 4):
            #向右移动
            self.y += 1
        self.fuel -= 1

    def attack(self):
        self.missile -= 1
    
    def fuel(self,fuel_count):
        self.fuel += fuel_count

#地图
class Map:
    def __init__(self,filepath):
        with open(filepath, 'r') as f:
            #读取地图大小
            line = f.readline()
            num_xy= [int(num) for num in line.split()]
            self.length = num_xy[0]
            self.width = num_xy[1]

            # 初始化地图网格
            self.map = [['' for _ in range(self.width)] for _ in range(self.length)]

            # 读取地图信息
            for i in range(self.length):
                line = f.readline()
                for j in range (self.width):
                    self.map[i][j]=line[j]
            #读取蓝方基地
            line = f.readline()
            self.num_of_blue = int(line) 
            self.BlueBases=[]
            for _ in range(self.num_of_blue):
                line = f.readline()
                base_xy=[int(num) for num in line.split()]
                line = f.readline()
                base_info=[int(num) for num in line.split()]
                self.BlueBases.append(BlueBase(base_xy[0],base_xy[1],base_info[0],
                                               base_info[1],base_info[2],base_info[3]))
            #读取红方基地
            line = f.readline()
            self.num_of_red = int(line) 
            self.RedBases=[]
            for _ in range (self.num_of_red):
                line = f.readline()
                base_xy=[int(num) for num in line.split()]
                line = f.readline()
                base_info=[int(num) for num in line.split()]
                self.RedBases.append(RedBase(base_xy[0],base_xy[1],base_info[0],
                                               base_info[1],base_info[2],base_info[3]))
            #读取飞机
            line = f.readline()
            self.num_of_plane = int(line) 
            self.Planes=[]
            for _ in range(self.num_of_plane):
                line = f.readline()
                plane_xy=[int(num) for num in line.split()]
                line = f.readline()
                plane_info=[int(num) for num in line.split()]
                self.Planes.append(Plane(_,plane_xy[0],plane_xy[1],plane_info[0],plane_info[1]))