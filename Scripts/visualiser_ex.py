import matplotlib.pyplot as plt
import numpy as np
import random

#Function return vector of vectors of coordinates for given number_of_points
#like: [ [x1,y1], [x2,y2], etc... ]
#ARGS: number_of_points - how many points create in this Y-axis? 
#      bounds - bounds for drawing window (just max X and max Y)
#      offset_x - space between each column of graph points
def get_coordinates(number_of_points, bounds,offset_x):
    points = []
    offset_y = bounds[1] / (number_of_points + 1)
    
    for i in range(0,number_of_points):
        points.append([offset_x, bounds[1] - offset_y * (i+1)])
    
    return points
#

#This one, given points vector (see above) prints
#one point in each of desired coordinates, with given "point_name" annotation
def draw_points(points,point_name):
    for i,coords in enumerate(points):
        #plot point in given coords
        plt.plot(coords[0],coords[1],"ko")
        #description for each point
        plt.annotate(point_name+str(i), #just to have x0, x1 etc ...
                    xy=(coords[0],coords[1]),
                    textcoords="offset points", #offset so that annotation
                    xytext=(-3.5, -15.0))       #appears below each point    
    #
#

#This one - give two points and line style
#converts given point to a format acceptable for plt.plot and connects them
def connect_two_points(p1,p2,line_style):
    x1, x2 = p1[0], p2[0]
    y1, y2 = p1[1], p2[1]
    
    plt.plot([x1,x2],[y1,y2],line_style)
#

#This function takes matrix of coincidence and two vectors of 
#points so that each point can be connected in an appropriate matter
def graph_connector(matrix,source,dest):
    for (x,y),val in np.ndenumerate(matrix): 
        if val == 1:
            connect_two_points(source[x],dest[y],'k-')
        if val == -1:
            connect_two_points(source[x],dest[y],'k--')


#Python's int main() ....
if __name__ == "__main__":
    
     
    """ 
    
    1. dorobic okregi by bylo ladnie o -- ( m ) -- o
    2. x --o dorobic
    3. indexy
    4. inne wpisywanie danych do macierzy
    
    """
    
    #max x and max y for our image
    bound_x = 10
    bound_y = 10

    #Creating arrays that contains information about edges
    
    """ -----------  MANUALLY ---------- """  
    A = np.array([1,1,1,
                  0,1,-1,
                   1,-1,0,
                   1,0,-1]).reshape(4,3)
                   
    C = np.array([1,-1,-1,0,
                   1,0,1,1,
                   1,1,0,-1]).reshape(3,4)
                   
    C = np.transpose(C)
    """ -----------  MANUALLY ----------  """
    
    
    
    """ -----------  RANDOMLY ----------  
    ACx = random.randint(2,5)
    Ay,Cy = random.randint(2,5),random.randint(2,5)
    
    A = np.random.randint(3,size=(ACx,Ay))-1
    C = np.random.randint(3,size=(ACx,Cy))-1
    
     -----------  RANDOMLY ----------  """
    
    if A.shape[0] != C.shape[0]:
        print("You need to check size of matrices!")
        exit()
    
    #From these matrices we need to create points coordinates
    x_points = get_coordinates(A.shape[1], (bound_x,bound_y),0.25 * bound_x)
    m_points = get_coordinates(A.shape[0], (bound_x,bound_y),0.25 * bound_x*2)
    y_points = get_coordinates(C.shape[1], (bound_x,bound_y),0.25 * bound_x*3)
    
    #initialization for plotting image and boundaries
    plt.figure("Just_a_ggenerator")
    plt.axis('off')
    plt.axis([0, bound_x, 0, bound_y])

    #draw points for each of classes - x - m - y
    draw_points(x_points,'x')
    draw_points(m_points,'m')
    draw_points(y_points,'y')

    #connect these points according to coincidence matrices
    graph_connector(A, m_points, x_points)
    graph_connector(C, m_points, y_points)
    
    
    #if you need to save it to a file
    plt.savefig("graph_name.pdf", bbox_inches='tight')
    

    plt.show()






