from collections import deque
import heapq
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
        
        if(base.fuel == 0 and base.missile == 0):
            for p in self.Planes : 
                if p.supply_target == base.id :
                    p.supply_target = -1
                    p.path = []
  


    def attack(self,plane : Plane, base : RedBase ):
        missile = base.defense if base.defense <= plane.missile else plane.missile
        if(missile == -1):
            missile = -1
        plane.attack(missile)
        base.suffer_attack(missile)
        target = (base.x,base.y)
        if base.x < plane.x:
            direction = 0
        elif base.x > plane.x:
            direction = 1
        elif base.y < plane.y:
            direction = 2
        elif base.y > plane.y:
            direction = 3

        print("attack" + " " + str(plane.id) + " " + str(direction) + " " + str(missile))  
        
        if(base.defense == 0):
            for p in self.Planes :
                if p.attack_target == base.id :
                    p.attack_target = -1
                    p.path = []
            self.map[base.x][base.y] = "."   
            base.defense = -1     
            self.lost_redbase += 1

    def move(self,plane : Plane, direction) :
        plane.move(direction);
        print("move" + " " + str(plane.id) + " " + str(direction))
     

    #寻找攻击目标
    def find_attack_target(self,plane):
        attack_target = -1
        attack_target_distance = 0
        # attack_target_w = 0
        # attack_path = None
        for redBase in self.RedBases:
            #除去以摧毁的基地
            if redBase.defense < 0:
                continue

            #计算该红方基地对于飞机的倾向性
            # value = redBase.value
            # defense = redBase.defense
            distance = self.distance_from_plane_to_base(plane, redBase)
            # w_red = value - ALPHA * defense - BETA * distance

            # 除去在移动范围外的基地
            # if distance > plane.fuel :
            #     continue

            #选择最近、价值最高的
            if (distance < attack_target_distance) or (attack_target == -1):
                attack_target = redBase.id
                attack_target_distance = distance
            elif distance == attack_target_distance and redBase.value > self.RedBases[attack_target].value :
                attack_target = redBase.id
                attack_target_distance = distance

            #如果倾向性更大或当前无目标
            # if w_red > attack_target_w or attack_target == -1 :
            #     now_attack_path = self.path_search(plane, redBase)
            #     if now_attack_path == None :
            #         continue
            #     attack_path = now_attack_path
            #     attack_target = redBase.id
            #     attack_target_w = w_red
        
        #plane.attack_target = attack_target



        return attack_target
    
    #寻找补给目的地
    def find_supply_target(self, plane:Plane, supply_type = 0):
        target = -1
        distance = 0
        fuel_count = 0
        missile_count = 0
        w_missile = 0
        # w_sup = 0

        # if supply_type == 0:
        #     f = 0.7
        #     m = 0
        #     d = 0.5
        # elif supply_type == 1:
        #     f = 0.5
        #     m = 0.3
        #     d = 0.5


        for BlueBase in self.BlueBases :
            #去除无补给的基地
            if BlueBase.fuel == 0 and BlueBase.missile == 0 :
                continue

            #当前所处基地
            if (BlueBase.x,BlueBase.y) == (plane.x,plane.y) :
                if BlueBase.fuel != 0 and supply_type == 0:
                    target = BlueBase.id
                    return target
                elif BlueBase.missile != 0 and supply_type == 1 :
                    target = BlueBase.id
                    return target
                continue
                

            now_distance = self.distance_from_plane_to_base(plane,BlueBase)

            #去除不在移动范围内的基地
            if(now_distance + 10> plane.fuel):
                continue
            
            now_fuel_count = plane.fuel_capacity if BlueBase.fuel >= plane.fuel_capacity - (plane.fuel - now_distance) else plane.fuel - now_distance + BlueBase.fuel
            now_missile_count = BlueBase.missile if BlueBase.missile < (plane.missile_capacity - plane.missile) else plane.missile_capacity 
            
            if(now_fuel_count == 0 and supply_type == 0):
                continue
            if(now_missile_count == 0 and supply_type == 1):
                continue
            #计算选择的倾向性
            # now_w_sup = f * now_fuel_count + m * now_missile_count - d * distance
            
            # if now_w_sup > w_sup :
            #     target = BlueBase.id
            #     w_sup = now_w_sup
            #     continue
            
            now_w_missile = 0.5 * now_fuel_count + 0.3 * now_missile_count 

            #缺油时以补油优先
            if supply_type == 0 :
                if now_fuel_count < fuel_count :
                    continue
                if now_fuel_count == fuel_count and now_distance > distance :
                    continue
            #不缺油时以补弹优先
            elif supply_type == 1:
                if now_w_missile < w_missile :
                    continue
                if now_w_missile == w_missile and now_distance > distance :
                    continue

            target = BlueBase.id
            fuel_count = now_fuel_count
            w_missile = now_w_missile
        
        return target
    
    def heuristic(self, a, b):
        """
        计算启发式函数值，使用曼哈顿距离。
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def path_search(self, plane: Plane, base: Base):
        """
        使用A*算法为飞机搜索路径。
        如果目标是蓝方基地，则直接到达基地所在坐标。
        如果目标是红方基地，则目的地为该基地四周的单元格（无其他红方基地）。
        """
        start = (plane.x, plane.y)  # 起点为飞机的当前位置

        if isinstance(base, BlueBase):
            goal = (base.x, base.y)
            goal_positions = [goal]  # 目标位置为蓝方基地的坐标
        elif isinstance(base, RedBase):
            goal = (base.x, base.y)
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            # 目标位置为红方基地周围的单元格
            goal_positions = [(goal[0] + d[0], goal[1] + d[1]) for d in directions]
            # 过滤掉不可到达的单元格，如墙壁和其他红方基地所在的位置
            goal_positions = [pos for pos in goal_positions if 0 <= pos[0] < self.length and 0 <= pos[1] < self.width and self.map[pos[0]][pos[1]] != '#' ]
        else:
            return None  # 无效的基地类型

        if start in goal_positions:
            return []  # 如果起点就在目标位置，直接返回空路径

        open_set = []  # 优先队列用于存储待探索的节点
        heapq.heappush(open_set, (0, start))  # 将起点加入队列，优先级为0
        came_from = {}  # 用于记录路径
        g_score = {start: 0}  # 起点的实际代价为0
        f_score = {start: min(self.heuristic(start, pos) for pos in goal_positions)}  # 启发式代价为起点到所有目标位置的最小值

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        direction_labels = [0, 1, 2, 3]  # 方向标签用于指示移动方向

        while open_set:
            _, current = heapq.heappop(open_set)  # 从队列中取出优先级最低的节点

            if current in goal_positions:
                path = []  # 如果当前节点是目标位置，重建路径
                while current in came_from:
                    current, direction = came_from[current]
                    if direction is not None:
                        path.append(direction)
                return path[::-1]  # 返回路径（从起点到目标）

            for idx, direction in enumerate(directions):
                neighbor = (current[0] + direction[0], current[1] + direction[1])  # 计算邻居节点的位置

                if 0 <= neighbor[0] < self.length and 0 <= neighbor[1] < self.width:  # 检查邻居节点是否在地图范围内
                    if self.map[neighbor[0]][neighbor[1]] == '#' and neighbor not in goal_positions:
                        continue  # 忽略墙壁单元格，除非它是目标位置

                    tentative_g_score = g_score[current] + 1  # 计算邻居节点的实际代价

                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:  # 如果找到更优的路径
                        came_from[neighbor] = (current, direction_labels[idx])  # 记录路径
                        g_score[neighbor] = tentative_g_score  # 更新实际代价
                        f_score[neighbor] = tentative_g_score + min(self.heuristic(neighbor, pos) for pos in goal_positions)  # 更新估计总代价
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))  # 将邻居节点加入队列

        return []  # 如果没有找到路径，返回None

    #寻找目标基地最近的补给点
    def less_supply_distance(self,red:RedBase,fuel:int) :
        supply_target = -1
        distance = -1
        for blue in self.BlueBases :
            now_distance = np.abs(blue.x - red.x) + np.abs(blue.y - red.y)

            if now_distance > fuel or blue.fuel <= 0:
                continue

            if(supply_target == -1) :
                supply_target = blue.id
                distance = now_distance
                continue
            
            if now_distance < distance:
                supply_target = blue.id
                distance = now_distance
        return distance
                

    def plane_control(self,plane:Plane):
        is_move = False

        while 1 :

            #补给状态
            if(plane.state == 0):
                #无补给目标则搜寻
                if(plane.supply_target == -1):
                    plane.supply_target = self.find_supply_target(plane)
                    if(plane.supply_target == -1):
                        return
                

                BBase = self.BlueBases[plane.supply_target]

                if (plane.path == None or len(plane.path) == 0) :
                    #如果已抵达目标
                    if (plane.x,plane.y) == (BBase.x,BBase.y):
                        self.supply(plane,BBase)
                        plane.supply_target = -1
                        plane.attack_target = -1
                        plane.state = 1
                        continue

                    plane.path = self.path_search(plane,BBase)
                #向目标移动
                if is_move == False and len(plane.path) > 0 :
                    self.move(plane,plane.path[0])
                    plane.path.pop(0)
                    is_move = True

                #移动后抵达目标
                if (plane.x,plane.y) == (BBase.x,BBase.y):
                    self.supply(plane,BBase)
                    plane.supply_target = -1
                    plane.attack_target = -1
                    plane.state = 1
                    continue

                #移动且未抵达目的地且无油
                if(plane.fuel == 0):
                    self.lost_plane += 1

                break
            
            #攻击状态
            elif plane.state == 1 :

                #无攻击目标则搜索
                if plane.attack_target == -1 :
                    plane.attack_target = self.find_attack_target(plane)
                
                RBase = self.RedBases[plane.attack_target]

                if plane.path == None or len(plane.path) == 0 :
                    plane.path = self.path_search(plane, RBase)
                    if (plane.path == None or len(plane.path) == 0) and (plane.missile > 0 and RBase.defense >= 0) :
                        self.attack(plane,RBase)
                        plane.supply_target = -1
                        plane.attack_target = -1
                        continue


                dis = len(plane.path) + self.less_supply_distance(RBase, plane.fuel - len(plane.path))



                if plane.fuel < dis + 20 and plane.fuel < plane.fuel_capacity / 2 :
                    plane.state = 0
                    plane.supply_target = self.find_supply_target(plane,0)
                    plane.path = self.path_search(plane, self.BlueBases[plane.supply_target])
                    continue
                
                if plane.missile <= 0 :
                    plane.state = 0
                    plane.supply_target = self.find_supply_target(plane,1)
                    plane.path = self.path_search(plane, self.BlueBases[plane.supply_target])
                    continue

                # #如果缺油，则进入补给
                # if len(plane.path) + 10 > plane.fuel :
                #     plane.state = 0
                #     plane.supply_target = self.find_supply_target(plane)
                #     plane.path = self.path_search(plane, self.BlueBases[plane.supply_target])
                #     continue
                # #如果缺弹，进行补给
                # if RBase.defense / 3 > plane.missile and plane.missile_capacity / 2 < plane.missile :
                #     plane.state = 0
                #     plane.supply_target = self.find_supply_target(plane, 1)
                #     plane.path = self.path_search(plane, self.BlueBases[plane.supply_target])
                #     continue

                #可移动则按照路径进行移动
                if len(plane.path) > 0 and is_move == False :
                    self.move(plane,plane.path[0])
                    plane.path.pop(0)
                    is_move = True
                #移动后抵达目标则进攻
                if len(plane.path) == 0 and (plane.missile > 0 and RBase.defense >= 0) :
                    self.attack(plane,RBase)
                    plane.supply_target = -1
                    plane.attack_target = -1
                    break

                break

                    




                



    # #确定一帧中飞机的行为
    # def control(self,plane:Plane):





    # #针对某一飞机,根据其缺油或缺弹状态确定其补给目标  supply_type为缺失类型 0为缺油，1为缺弹，2为都缺
    # def find_supply_target(self,plane,supply_type = 2):
    #     supply_target = -1
    #     supply_distance = -1
    #     supply_fuel = 0
    #     supply_missile = 0
    #     supply_path = None

    #     for blueBase in self.BlueBases:

    #         if(blueBase.fuel == 0 and blueBase.missile == 0 ):
    #             continue

    #         if (blueBase.x,blueBase.y) == (plane.x,plane.y):
    #             supply_target = blueBase.id
    #             now_supply_path = self.path_search(plane,blueBase)
    #             break

    #         now_supply_distance = self.distance_from_plane_to_base(plane, blueBase)

    #         if(now_supply_distance > plane.fuel) :
    #             continue

    #         ask_missile = plane.missile_capacity - plane.missile

    #         if now_supply_distance > plane.fuel:
    #             continue

    #         if blueBase.fuel > plane.fuel_capacity - (plane.fuel - now_supply_distance):
    #             now_supply_fuel = 1
    #         else:
    #             now_supply_fuel = 0
            
    #         if blueBase.missile > ask_missile:
    #             now_supply_missile = 1
    #         else:
    #             now_supply_missile = 0

    #         #当前无目标
    #         if supply_target == -1:
    #             supply_target = blueBase.id
    #             supply_distance = now_supply_distance
    #             supply_fuel = now_supply_fuel
    #             supply_missile = now_supply_missile
    #             continue
    #         #缺油   优先选能补满油 其次选最近
    #         if supply_type == 0 :
    #             if supply_fuel == 0 :
    #                 if now_supply_fuel == 0 and now_supply_distance > supply_distance :
    #                     continue
    #             elif supply_fuel == 1 :
    #                 if now_supply_fuel == 0 :
    #                     continue
    #                 elif now_supply_fuel == 1 :
    #                     if now_supply_distance > supply_distance :
    #                         continue

    #         #缺弹   优先选能补满弹  其次选最近
    #         elif supply_type == 1 :
    #             if supply_missile == 0 :
    #                 if now_supply_missile == 0 and now_supply_distance > supply_distance :
    #                     continue
    #             elif supply_missile == 1 :
    #                 if now_supply_missile == 0 :
    #                     continue
    #                 elif now_supply_missile == 1 :
    #                     if now_supply_distance > supply_distance :
    #                         continue

    #         #都缺   优先都补满   其次选能补满油  然后能补满弹  最后距离最近
    #         elif supply_type == 2 :
    #             if supply_fuel == 1 and supply_missile == 1 :
    #                 if supply_fuel != 1 or supply_missile != 1 or now_supply_distance > supply_distance :
    #                     continue

    #             elif supply_fuel == 1 and now_supply_fuel == 1 :
    #                 if now_supply_distance > supply_distance :
    #                     continue

    #             elif supply_fuel == 1 and now_supply_fuel == 0 :
    #                 continue
                
    #             elif supply_fuel == 0 and now_supply_fuel == 0 :
    #                 if now_supply_distance > supply_distance :
    #                     continue

    #             elif supply_missile == 1 and now_supply_missile == 1:
    #                 if now_supply_distance > supply_distance :
    #                     continue

    #             elif supply_missile == 1 and now_supply_missile == 0 :
    #                 continue 

    #             elif supply_missile == 0 and now_supply_missile == 0 :
    #                 if now_supply_distance > supply_distance :
    #                     continue


    #         else:
    #             return -1
            
    #         now_supply_path = self.path_search(plane,blueBase)
    #         if now_supply_path == None :
    #             continue

    #         supply_target = blueBase.id
    #         supply_distance = now_supply_distance
    #         supply_fuel = now_supply_fuel
    #         supply_missile = now_supply_missile    
    #         supply_path = now_supply_path
            
    #     plane.supply_target = supply_target
    #     return supply_path;

    #目标路径查询    
    # def path_search(self, plane, base):
    #     start = (plane.x, plane.y)
    #     goal = (base.x, base.y)
    #     grid_size = (self.length ,self.width)
        
    #     # 定义四个方向的移动（上下左右）
    #     directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    #     direction_labels = ['U', 'D', 'L', 'R']  # 用于表示方向的标签

    #     # 初始化队列和访问记录
    #     queue = deque([start])
    #     visited = set()
    #     visited.add(start)

    #     # 记录路径和方向的字典
    #     parent = {start: (None, None)}

    #     while queue:
    #         current = queue.popleft()

    #         # 如果到达目标，构建路径
    #         if current == goal:
    #             path = []
    #             directions_path = []
    #             while current:
    #                 current, direction = parent[current]
    #                 if direction is not None:
    #                     directions_path.append(direction)
    #             return directions_path[::-1]  # 反转路径

    #         # 遍历四个方向
    #         for idx, direction in enumerate(directions):
    #             neighbor = (current[0] + direction[0], current[1] + direction[1])

    #             # 检查邻居是否在网格范围内，且没有被访问过
    #             if (0 <= neighbor[0] < grid_size[0] and 0 <= neighbor[1] < grid_size[1] 
    #             and neighbor not in visited ):
    #                 if self.map[neighbor[0]][neighbor[1]] != "#" or neighbor == goal :
    #                     queue.append(neighbor)
    #                     visited.add(neighbor)
    #                     parent[neighbor] = (current, idx)

    #     return None  # 如果没有找到路径
       

    #def plane_control(self, plane:Plane):
        # x = plane.x 
        # y = plane.y
        # is_move = False
        # while 1:
        #     #攻击状态
        #     if plane.state == 1 :
        #         #无攻击目标
        #         if plane.attack_target == -1 :
        #             plane.path = self.find_attack_target(plane)
        #         #找不到攻击目标
        #         if plane.path == None :
        #             break

        #         base = self.RedBases[plane.attack_target]

        #         #根据当前油料和弹药的缺失状态判断是否进入补给状态
        #         if plane.fuel <= 30 and (plane.missile <= self.RedBases[plane.attack_target].defense/2
        #                                   and plane.missile < plane.missile_capacity/3) :
        #             plane.state = 0
        #             plane.path = self.find_supply_target(plane,2)
        #             continue
        #         elif plane.fuel <= 30 :
        #             plane.state = 0
        #             plane.path = self.find_supply_target(plane,0)
        #             continue
        #         elif plane.missile <= self.RedBases[plane.attack_target].defense/2 and plane.missile < plane.missile_capacity/3 :
        #             plane.state = 0
        #             plane.path = self.find_supply_target(plane,1)
        #             continue

        #         #如果该帧未移动且存在移动路径，移动
        #         if len(plane.path) > 1 and is_move == False and plane.fuel > 0 :
        #             self.move(plane,plane.path[0])
        #             plane.path.remove(plane.path[0])
        #             is_move = True
        #         #抵达目标周围，攻击
        #         if len(plane.path) == 1 :
        #             self.attack(plane,base,plane.path[0])
        #             plane.path = []
        #             continue

        #         if(plane.fuel == 0):
        #             plane.state = 0
        #             plane.path = self.find_supply_target(plane,2)
        #             continue

        #         break

        #     #补给状态
        #     if plane.state == 0 :

        #         #无补给目标
        #         if plane.supply_target == -1 :
        #             plane.path = self.find_supply_target(plane,2)
                    
        #         base = self.BlueBases[plane.supply_target]

        #         #位于补给点
        #         if (x,y) == (base.x, base.y) :
        #             self.supply(plane,base)
        #             plane.supply_target = -1
        #             plane.state = 1
        #             plane.path = self.find_attack_target(plane)
        #             continue

        #         #无可达补给点
        #         if plane.path == None :
        #             plane.state = 1
        #             continue

        #         #向补给点移动
        #         if len(plane.path) > 0 and is_move == False and plane.fuel > 0 :
        #             self.move(plane,plane.path[0])
        #             plane.path.remove(plane.path[0])
        #             is_move = True
        #             continue

                
        #         break

        #     if plane.fuel == 0 :
        #         break


    
