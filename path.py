import math
import numpy as np
import matplotlib.pyplot as plt

show_animation = True

class AStarPlanner:

    def __init__(self, ox, oy, resolution, rr):

        self.resolution = resolution   # grid resolution [m]
        self.rr = rr       # robot radius [m]
        self.calc_obstacle_map(ox, oy)
        self.motion = self.get_motion_model()


    # ����һ���ڵ��࣬�ڵ����Ϣ������xy���꣬cost����,parent_index
    class Node:
        def __init__(self, x, y , cost, parent_index):
            self.x = x    # index of grid
            self.y = y
            self.cost = cost  # g(n)
            self.parent_index = parent_index   # index of previous Node

        def __str__(self):    
            return str(self.x) + "," + str(self.y) + "," + str(
                self.cost) + "," + str(self.parent_index)
 

    # ����planning������������sx,sy,gx,gy, ����pathx,pathy(���յ�·��)
    def planning(self, sx, sy, gx, gy):
        """
        1��sx = nstart  sy = ngoal
        2��open_set  closed_set
        3��open_set = nstart 
        4����open���д�����С���ӽڵ�=��ǰ�ڵ㣬����plot�϶�̬��ʾ����esc�˳�
        5�������ǰ�ڵ����ngoal����ʾ�ҵ�Ŀ���
        6��ɾ��open���е����ݣ���ӵ�closed����
        7�������˶�ģ�Ͷ���������ʽ
        8��pathx,pathy = ����·��(����ngoal,closed_set)������pathx,pathy
        """

        # 1��sx = nstart  sy = ngoal  ��ʼ��nstart��ngoal������Ϊһ���ڵ㣬����ڵ�ȫ����Ϣ
        nstart = self.Node(self.calc_xyindex(sx, self.minx),  # position min_pos   2 (2.5)
                           self.calc_xyindex(sy, self.miny),  # 2 (2.5)
                           0.0,
                           -1)
        ngoal = self.Node(self.calc_xyindex(gx, self.minx),
                           self.calc_xyindex(gy, self.miny),
                           0.0,
                           -1)
        # 2��open��closed���趨Ϊ�ֵ�
        # 3��������open�� 
        open_set, closed_set = dict(), dict()   # key - value: hash��
        open_set[self.calc_grid_index(nstart)] = nstart   

        while 1:
            if len(open_set) == 0:
                print("Open_set is empty...")
                break

        # 4����open���д�����С���ӽڵ� = ��ǰ�ڵ㣬����plot�϶�̬��ʾ����esc�˳�  
          
            # f(n)=g(n)+w(n)*h(n)  ʵ�ʴ���+Ȩ��ϵ��*Ԥ������  
            c_id = min(open_set, key=lambda o: open_set[o].cost + self.calc_heuristic(ngoal, open_set[o]))
            current = open_set[c_id]  

            # ����ǰ�ڵ���ʾ����
            if show_animation:
                plt.plot(self.calc_grid_position(current.x, self.minx),
                         self.calc_grid_position(current.y, self.miny),
                         "xc")   # ��ɫx ������
                # ��esc�˳�
                plt.gcf().canvas.mpl_connect('key_release_event',
                                              lambda event: [exit(0) if event.key == 'escape' else None]
                                            )
                if len(closed_set.keys()) % 10 == 0:
                    plt.pause(0.001)

            if current.x == ngoal.x and current.y == ngoal.y:
                print("Find goal!")
                ngoal.parent_index = current.parent_index
                print("ngoal_parent_index:",ngoal.parent_index)
                ngoal.cost = current.cost
                print("ngoal_cost:",ngoal.cost)
                break

            # ɾ��open���е�c_id���ӽڵ�,����current��ӵ�closed_set
            del open_set[c_id]
            closed_set[c_id] = current

            # ����motion model��դ����չ��Ҳ����������ʽ���ɽ��иĽ�����ʹ��˫��������JPS��
            for move_x, move_y, move_cost in self.motion:
                node = self.Node(current.x + move_x,    # ��ǰx+motion�б��е�0��Ԫ��dx
                                 current.y + move_y,
                                 current.cost + move_cost,c_id)
                n_id = self.calc_grid_index(node)   # ���ظýڵ�λ��index

                # ����ڵ㲻��ͨ��������
                if not self.verify_node(node):
                    continue

                if n_id in closed_set:
                    continue

                if n_id not in open_set:
                    open_set[n_id] = node   # ֱ�Ӽ���a new node
                else:
                    if open_set[n_id].cost > node.cost:
                        open_set[n_id] = node    # This path is the best until now. record it

        pathx, pathy = self.calc_final_path(ngoal, closed_set) 
        
        return pathx, pathy

    
    def calc_final_path(self, ngoal, closedset):    # ����Ŀ����closed��������������õ��������е�xy�б�
        pathx, pathy = [self.calc_grid_position(ngoal.x, self.minx)], [
                        self.calc_grid_position(ngoal.y, self.miny)]
        parent_index = ngoal.parent_index
        while parent_index != -1:
            n = closedset[parent_index]
            pathx.append(self.calc_grid_position(n.x, self.minx))
            pathy.append(self.calc_grid_position(n.y, self.miny))
            parent_index = n.parent_index

        return pathx, pathy


                

    @staticmethod  # ��̬������calc_heuristic�������ô���self����ΪҪ�����޸�����������Ŀ����Ϊ������Ķ���
    def calc_heuristic(n1, n2):  # n1: ngoal��n2: open_set[o]     
        h =  math.hypot(n1.x - n2.x, n1.y - n2.y)
        if h > 18:
            w = 3
        else:
            w = 0.8 
        h = h * w
       
        return h


    # �õ�ȫ�ֵ�ͼ�еľ�������: �����ͼ����С���ϰ����pos��index
    def calc_grid_position(self, index, minpos):   
        pos = index * self.resolution + minpos
        return pos

    # λ��ת��Ϊ��դ���СΪ��λ������: ����position,min_pos
    def calc_xyindex(self, position, min_pos):
        return round((position - min_pos) / self.resolution)  # (��ǰ�ڵ�-��С��������)/�ֱ���=pos_index  round������������ȡ��

    # ����դ���ͼ�ڵ��index�� ����ĳ���ڵ�
    def calc_grid_index(self, node):
        return (node.y - self.miny) * self.xwidth + (node.x - self.minx)   

    # ��֤�Ƿ�Ϊ��ͨ�нڵ�
    def verify_node(self, node):
        posx = self.calc_grid_position(node.x, self.minx)
        posy = self.calc_grid_position(node.y, self.miny)

        if posx < self.minx:
            return False
        elif posy < self.miny:
            return False
        elif posx >= self.maxx:
            return False
        elif posy >= self.maxy:
            return False

        if self.obmap[int(node.x)][int(node.y)]:
            return False

        return True

    def calc_obstacle_map(self, ox, oy):
        self.minx = round(min(ox))    # ��ͼ�е��ٽ�ֵ -10
        self.miny = round(min(oy))    # -10
        self.maxx = round(max(ox))    # 60 
        self.maxy = round(max(oy))    # 60
        print("minx:", self.minx)
        print("miny:", self.miny)
        print("maxx:", self.maxx)
        print("maxy:", self.maxy)

        self.xwidth = round((self.maxx - self.minx) / self.resolution)   # 35
        self.ywidth = round((self.maxy - self.miny) / self.resolution)   # 35
        print("xwidth:", self.xwidth)
        print("ywidth:", self.ywidth)

        self.obmap = [[False for i in range(int(self.ywidth))]
                       for i in range(int(self.xwidth))]
        for ix in range(int(self.xwidth)):
            x = self.calc_grid_position(ix, self.minx)
            for iy in range(int(self.ywidth)):
                y = self.calc_grid_position(iy, self.miny)
                for iox, ioy in zip(ox, oy):  #��ox,oy�����Ԫ�飬�����б�������
                    d = math.hypot(iox - x, ioy - y)  
                    if d <= self.rr:          #����С�ڳ����뾶��������ͨ�������ᴩԽ�ϰ���
                        self.obmap[ix][iy] = True
                        break



    @staticmethod
    def get_motion_model():
        # dx, dy, cost
        motion = [
                    [1, 0, 1],
                    [0, 1, 1],
                   # [-1, 0, 1],
                    [0, -1, 1],
                    [1, 1, math.sqrt(2)],
                    [1, -1, math.sqrt(2)]
                   # [-1, 1, math.sqrt(2)],
                   # [-1, -1, math.sqrt(2)]    
                 ]
        
        return motion




def main():
    print(__file__ + '  start!')
    plt.title("Astar")
    
    # start and goal position  [m]
    sx = -5.0
    sy = -5.0
    gx = 50
    gy = 50
    grid_size = 2.0
    robot_radius = 1.0

    # obstacle positions
    ox, oy = [],[]
    for i in range(-10, 60): 
        ox.append(i)
        oy.append(-10)      # y����-10��һ��-10~60��������ӵ��б���ʾΪ��ɫ�ϰ���
    for i in range(-10, 60):
        ox.append(i)
        oy.append(60)       # y����60��һ��-10~60��������ӵ��б���ʾΪ��ɫ�ϰ���
    for i in range(-10, 61):
        ox.append(-10)
        oy.append(i)        # x����-10��һ��-10~61��������ӵ��б���ʾΪ��ɫ�ϰ���
    for i in range(-10, 61):
        ox.append(60)
        oy.append(i)        # x����60��һ��-10~61��������ӵ��б���ʾΪ��ɫ�ϰ���
    for i in range(-10, 40):
        ox.append(20)
        oy.append(i)        # x����20��һ��-10~40��������ӵ��б���ʾΪ��ɫ�ϰ���
    for i in range(0, 40):
        ox.append(40)
        oy.append(60 - i)   # x����40��һ��20~60��������ӵ��б���ʾΪ��ɫ�ϰ���



    if show_animation:
        plt.plot(ox,oy,".k") # ��ɫ.       �ϰ���
        plt.plot(sx,sy,"og") # ��ɫԲȦ    ��ʼ����
        plt.plot(gx,gy,"xb") # ��ɫx       Ŀ���
        plt.grid(True)
        plt.axis('equal')  # ����դ��ĺ�������̶�һ��


    a_star = AStarPlanner(ox, oy, grid_size ,robot_radius)  # grid_size=resolution ��ʼ���д���Ĳ���
    pathx, pathy = a_star.planning(sx, sy, gx, gy)  # ��ʼ����������괫�뺯�����д���󣬵õ�pathx,pathy�����չ滮����·������


    if show_animation:
        plt.plot(pathx, pathy, "-r")  # ��ɫֱ�� ����·��
        plt.show()
        plt.pause(0.001)   # ��̬��ʾ


if __name__ == '__main__':
    main()