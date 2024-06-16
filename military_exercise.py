from collections import deque
import numpy as np

ALPHA = 0.2     #防御影响因子
BETA  = 0.5     #距离影响因子

#基地类
class Base:
    def __init__(self,id,x,y,fuel,missile,defense,value):
        self.id = id
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
    def suffer_attack(self,count):
        self.defense -= count

#蓝方基地
class BlueBase(Base):
     def __init__(self ,id ,x, y, fuel, missile, defense, value):
        super().__init__(id, x, y, fuel, missile, defense, value)
        self.factions=0

#红方基地
class RedBase(Base):
    def __init__(self ,id , x, y, fuel, missile, defense, value):
        super().__init__(id ,x, y, fuel, missile, defense, value)
        self.factions=1


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
        self.path = []
        
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

    def attack(self,missile):
        self.missile -= missile
    
    def get_fuel(self,fuel_count):
        self.fuel += fuel_count

    def get_missile(self,missile_count):
        self.missile += missile_count

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
                self.BlueBases.append(BlueBase(_,base_xy[0],base_xy[1],base_info[0],
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
                self.RedBases.append(RedBase(_,base_xy[0],base_xy[1],base_info[0],
                                               base_info[1],base_info[2],base_info[3]))
            #读取飞机
            line = f.readline()
            self.num_of_plane = int(line) 
            self.Planes=[]
            for _ in range(self.num_of_plane):
                line = f.readline()
                plane_info=[int(num) for num in line.split()]
                self.Planes.append(Plane(_,plane_info[0],plane_info[1],plane_info[2],plane_info[3]))
            
            self.lost_plane = 0
            self.lost_redbase = 0


    def distance_from_plane_to_base(self,plane,base):
        distance = np.abs(base.x - plane.x) + np.abs(base.y - plane.y)
        return distance

    #针对某一飞机确定其攻击目标
    def find_attack_target(self,plane):
        attack_target = -1
        attack_target_w = 0
        attack_path = None
        for redBase in self.RedBases:

            if redBase.defense < 0:
                continue

            #计算该红方基地对于飞机的倾向性
            value = redBase.value
            defense = redBase.defense
            distance = self.distance_from_plane_to_base(plane, redBase)
            w_red = value - ALPHA * defense - BETA * distance

            if(distance > plane.fuel):
                continue

            #如果倾向性更大或当前无目标
            if w_red > attack_target_w or attack_target == -1 :
                now_attack_path = self.path_search(plane, redBase)
                if now_attack_path == None :
                    continue
                attack_path = now_attack_path
                attack_target = redBase.id
                attack_target_w = w_red
        
        plane.attack_target = attack_target
        return attack_path
    
    #针对某一飞机,根据其缺油或缺弹状态确定其补给目标  supply_type为缺失类型 0为缺油，1为缺弹，2为都缺
    def find_supply_target(self,plane,supply_type = 2):
        supply_target = -1
        supply_distance = -1
        supply_fuel = 0
        supply_missile = 0
        supply_path = None

        for blueBase in self.BlueBases:

            if(blueBase.fuel == 0 and blueBase.missile == 0 ):
                continue

            if (blueBase.x,blueBase.y) == (plane.x,plane.y):
                supply_target = blueBase.id
                now_supply_path = self.path_search(plane,blueBase)
                break

            now_supply_distance = self.distance_from_plane_to_base(plane, blueBase)

            if(now_supply_distance > plane.fuel) :
                continue

            ask_missile = plane.missile_capacity - plane.missile

            if now_supply_distance > plane.fuel:
                continue

            if blueBase.fuel > plane.fuel_capacity - (plane.fuel - now_supply_distance):
                now_supply_fuel = 1
            else:
                now_supply_fuel = 0
            
            if blueBase.missile > ask_missile:
                now_supply_missile = 1
            else:
                now_supply_missile = 0

            #当前无目标
            if supply_target == -1:
                supply_target = blueBase.id
                supply_distance = now_supply_distance
                supply_fuel = now_supply_fuel
                supply_missile = now_supply_missile
                continue
            #缺油   优先选能补满油 其次选最近
            if supply_type == 0 :
                if supply_fuel == 0 :
                    if now_supply_fuel == 0 and now_supply_distance > supply_distance :
                        continue
                elif supply_fuel == 1 :
                    if now_supply_fuel == 0 :
                        continue
                    elif now_supply_fuel == 1 :
                        if now_supply_distance > supply_distance :
                            continue

            #缺弹   优先选能补满弹  其次选最近
            elif supply_type == 1 :
                if supply_missile == 0 :
                    if now_supply_missile == 0 and now_supply_distance > supply_distance :
                        continue
                elif supply_missile == 1 :
                    if now_supply_missile == 0 :
                        continue
                    elif now_supply_missile == 1 :
                        if now_supply_distance > supply_distance :
                            continue

            #都缺   优先都补满   其次选能补满油  然后能补满弹  最后距离最近
            elif supply_type == 2 :
                if supply_fuel == 1 and supply_missile == 1 :
                    if supply_fuel != 1 or supply_missile != 1 or now_supply_distance > supply_distance :
                        continue

                elif supply_fuel == 1 and now_supply_fuel == 1 :
                    if now_supply_distance > supply_distance :
                        continue

                elif supply_fuel == 1 and now_supply_fuel == 0 :
                    continue
                
                elif supply_fuel == 0 and now_supply_fuel == 0 :
                    if now_supply_distance > supply_distance :
                        continue

                elif supply_missile == 1 and now_supply_missile == 1:
                    if now_supply_distance > supply_distance :
                        continue

                elif supply_missile == 1 and now_supply_missile == 0 :
                    continue 

                elif supply_missile == 0 and now_supply_missile == 0 :
                    if now_supply_distance > supply_distance :
                        continue


            else:
                return -1
            
            now_supply_path = self.path_search(plane,blueBase)
            if now_supply_path == None :
                continue

            supply_target = blueBase.id
            supply_distance = now_supply_distance
            supply_fuel = now_supply_fuel
            supply_missile = now_supply_missile    
            supply_path = now_supply_path
            
        plane.supply_target = supply_target
        return supply_path;

    #目标路径查询    
    def path_search(self, plane, base):
        start = (plane.x, plane.y)
        goal = (base.x, base.y)
        grid_size = (self.length ,self.width)
        
        # 定义四个方向的移动（上下左右）
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        direction_labels = ['U', 'D', 'L', 'R']  # 用于表示方向的标签

        # 初始化队列和访问记录
        queue = deque([start])
        visited = set()
        visited.add(start)

        # 记录路径和方向的字典
        parent = {start: (None, None)}

        while queue:
            current = queue.popleft()

            # 如果到达目标，构建路径
            if current == goal:
                path = []
                directions_path = []
                while current:
                    current, direction = parent[current]
                    if direction is not None:
                        directions_path.append(direction)
                return directions_path[::-1]  # 反转路径

            # 遍历四个方向
            for idx, direction in enumerate(directions):
                neighbor = (current[0] + direction[0], current[1] + direction[1])

                # 检查邻居是否在网格范围内，且没有被访问过
                if (0 <= neighbor[0] < grid_size[0] and 0 <= neighbor[1] < grid_size[1] 
                and neighbor not in visited ):
                    if self.map[neighbor[0]][neighbor[1]] != "#" or neighbor == goal :
                        queue.append(neighbor)
                        visited.add(neighbor)
                        parent[neighbor] = (current, idx)

        return None  # 如果没有找到路径

    def supply(self, plane : Plane, base : BlueBase):
        fuel = plane.fuel_capacity - plane.fuel if (plane.fuel_capacity - plane.fuel) <= base.fuel else base.fuel
        missile = plane.missile_capacity - plane.missile if(plane.missile_capacity - plane.missile) <= base.missile else base.missile
        
        if fuel > 0 :
            plane.get_fuel(fuel)
            base.refuel_for_plane(fuel)
            print("fuel" + " " + str(plane.id) + " " + str(fuel))
        if missile > 0 :
            plane.get_missile(missile)
            base.reload_missile(missile)
            print("missile" + " " + str(plane.id) + " " + str(missile))
        
        if(base.fuel == 0 or base.missile == 0):
            for p in self.Planes : 
                if p.supply_target == base.id :
                    p.supply_target == -1
            if(base.fuel == 0 and base.missile == 0):
                self.map[base.x][base.y] = "."    


    def attack(self,plane : Plane, base : RedBase ,direction):
        missile = base.defense if base.defense <= plane.missile else plane.missile
        plane.attack(missile)
        base.suffer_attack(missile)
        print("attack" + " " + str(plane.id) + " " + str(direction) + " " + str(missile))  
        
        if(base.defense == 0):
            for p in self.Planes :
                if p.attack_target == base.id :
                    p.attack_target = -1
            self.map[base.x][base.y] = "."   
            base.defense = -1     
            self.lost_redbase += 1

    def move(self,plane : Plane, direction) :
        plane.move(direction);
        if(plane.fuel == 0):
            self.lost_plane += 1
        print("move" + " " + str(plane.id) + " " + str(direction))
            

    def plane_control(self, plane:Plane):
        x = plane.x 
        y = plane.y
        is_move = False
        while 1:
            
            if plane.state == 1 :
                if plane.attack_target == -1 :
                    plane.path = self.find_attack_target(plane)

                if plane.path == None :
                    break

                base = self.RedBases[plane.attack_target]

                if plane.fuel <= 30 and (plane.missile <= self.RedBases[plane.attack_target].defense/2
                                          and plane.missile < plane.missile_capacity/3) :
                    plane.state = 0
                    plane.path = self.find_supply_target(plane,2)
                    continue
                elif plane.fuel <= 30 :
                    plane.state = 0
                    plane.path = self.find_supply_target(plane,0)
                    continue
                elif plane.missile <= self.RedBases[plane.attack_target].defense/2 and plane.missile < plane.missile_capacity/3 :
                    plane.state = 0
                    plane.path = self.find_supply_target(plane,1)
                    continue

                if len(plane.path) > 1 and is_move == False :
                    self.move(plane,plane.path[0])
                    plane.path.remove(plane.path[0])
                    is_move = True
                
                elif len(plane.path) == 1 :
                    self.attack(plane,base,plane.path[0])
                    plane.path = []
                    continue

                break


            if plane.state == 0 :
                if plane.supply_target == -1 :
                    plane.path = self.find_supply_target(plane,2)
                base = self.BlueBases[plane.supply_target]


                if (x,y) == (base.x, base.y) :
                    self.supply(plane,base)
                    plane.supply_target = -1
                    plane.state = 1
                    plane.path = self.find_attack_target(plane)
                    continue

                if plane.path == None :
                    plane.state = 1
                    continue


                if len(plane.path) > 0 and is_move == False :
                    self.move(plane,plane.path[0])
                    plane.path.remove(plane.path[0])
                    is_move = True
                    continue

                
                break

            if plane.fuel == 0 :
                break


    
