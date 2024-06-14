import numpy as np

ALPHA = 0.2     #防御影响因子
BETA  = 0.5     #距离影响因子

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
        self.id=id  #飞机id
        self.x=x    #飞机x坐标
        self.y=y    #飞机y坐标
        self.fuel_capacity=fuel_capacity    #飞机油箱容量
        self.fuel = 0   #飞机当前油量
        self.missile_capacity=missile_capacity  #飞机弹药容量
        self.missile = 0    #飞机当前弹药量
        self.state = 0      #飞机状态，0为补给状态，1为攻击状态，初始为补给状态
        self.attack_target = -1     #飞机攻击目标  为红方基地id，初始为-1
        self.supply_target = -1     #飞机补给目标  为蓝方基地id，初始为-1

        
    #上下左右 0123
    def move(self,direction):
        if(direction == 0):
            #向上方移动
            self.x -= 1
        elif(direction == 1):
            #向下方移动
            self.x += 1
        elif(direction == 2):
            #向左移动
            self.y -= 1
        elif(direction == 3):
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

    #针对某一飞机确定其攻击目标
    def find_attack_target(self,plane_id):
        plane = self.Planes[plane_id]
        attack_target = -1
        attack_target_w = 0

        for redBase in self.RedBases:
            #计算该红方基地对于飞机的倾向性
            value = redBase.value
            defense = redBase.defense
            distance = np.abs(redBase.x - plane.x) + np.abs(redBase.y - plane.y)
            w_red = value - ALPHA * defense - BETA * distance
            #如果倾向性更大或当前无目标
            if w_red > attack_target_w or attack_target == -1 :
                attack_target = redBase.id
                attack_target_w = w_red
        
        plane.attack_target = attack_target
        return 
    
    def find_supply_target(self,plane_id):
        



