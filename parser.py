from parse import *

margin = 10

# Function parseMorphologies
# Take multiple morphologies and put them together in a cube
#   Inputs:
#     morphologies : list of morphologies .geo files
#     type         : type of positioning
#                       0 : simple translation on the X axys
#                       1 : positioning using TODO ADD NAME
#     factor       : scaling factor for the point size
def parseMorphologies(morphologies, type, factor):
    counter_points = 0
    counter_lines  = 0
    geo            = ''
    dmg            = ''
    minPoint       = [100000,100000,100000]
    maxPoint       = [-100000,-100000,-100000]
    txt            = str(len(morphologies)) + '\n'
    for i in range(len(morphologies)):
        actual_counter_points = counter_points
        actual_counter_lines  = counter_lines
        limitPoint            = maxPoint[0] - minPoint[0] #Suppose that every neuron have aproximatelly the same size TODO Correct this
        content               = []
        txt_points            = ''
        txt_lines             = ''

        with open(morphologies[i]) as f:
            content = f.read().split('\n')
        for j in range(len(content)):
            cleanedLine = content[j].replace("{","").replace("}","").replace(" ","")
            print(str(j)+": "+cleanedLine)
            point_parse = parse("Point({p})={x},{y},{z},{s};",cleanedLine)
            line_parse = parse("Line({l})={p1},{p2};",cleanedLine)
            if (point_parse != None):
                # Setting new values TODO Translation and rotation here
                p = int(point_parse['p']) + actual_counter_points
                x = float(point_parse['x']) + i * limitPoint
                y = float(point_parse['y'])
                z = float(point_parse['z'])
                s = float(point_parse['s']) * factor

                # Checking Min, Max
                checkX = checkMinMax(x,minPoint[0],maxPoint[0])
                minPoint[0] = checkX[0]
                maxPoint[0] = checkX[1]
                checkX = checkMinMax(y,minPoint[1],maxPoint[1])
                minPoint[1] = checkX[0]
                maxPoint[1] = checkX[1]
                checkX = checkMinMax(z,minPoint[2],maxPoint[2])
                minPoint[2] = checkX[0]
                maxPoint[2] = checkX[1]

                # Printing
                geo += 'Point(' + str(p) + ') = {' + str(x) + ',' + str(y) + ',' + str(z) + ',' + str(s) + '};\n'
                dmg += 'Point[' + str(p) + '] = gmod::new_point3(gmod::Vector{' + str(x) + ',' + str(y) + ',' + str(z) + '},' + str(s) + ');\n'
                txt_points += '\n'+ str(p)

                counter_points += 1

            elif (line_parse != None):
                # Setting new values
                l = int(line_parse['l']) + actual_counter_lines
                p1 = int(line_parse['p1']) + actual_counter_points
                p2 = int(line_parse['p2']) + actual_counter_points

                # Printing
                geo += 'Line(' + str(l) + ') = {' + str(p1) + ',' + str(p2) + '} ;\n'
                dmg += 'gmod::add_to_group(g, gmod::new_line2(Point[' + str(p1) + '], Point[' + str(p2) + ']));\n'
                txt_lines += ' '+ str(l)

                counter_lines += 1
        txt += str(counter_points - actual_counter_points) + txt_points + '\n'
        txt += str(counter_lines - actual_counter_lines) + txt_lines + '\n'
    # Main part pour Gmodel to generate .dmg
    dmg =   "#include <gmodel.hpp>\n"+"#include <minidiff.hpp>\n"+"\n"+"int main()\n"+"   std::vector<gmod::PointPtr> Point;\n"+"   auto g = gmod::new_group();\n"+"   Point.resize(" + str(counter_points) + ");\n"+"\n"+ dmg

    # Cube calculation
    cubeSize = max(maxPoint[0]-minPoint[0],maxPoint[1]-minPoint[1],maxPoint[2]-minPoint[2])/2 + margin
    middle = [(maxPoint[0]+minPoint[0])/2,(maxPoint[1]+minPoint[1])/2,(maxPoint[2]+minPoint[2])/2]

    # Cube generation .geo
    geo += newPoint(middle[0]-cubeSize, middle[1]-cubeSize, middle[2]-cubeSize,cubeSize/2,1)
    geo += newPoint(middle[0]+cubeSize, middle[1]-cubeSize, middle[2]-cubeSize,cubeSize/2,2)
    geo += newPoint(middle[0]+cubeSize, middle[1]+cubeSize, middle[2]-cubeSize,cubeSize/2,3)
    geo += newPoint(middle[0]-cubeSize, middle[1]+cubeSize, middle[2]-cubeSize,cubeSize/2,4)
    geo += newPoint(middle[0]-cubeSize, middle[1]-cubeSize, middle[2]+cubeSize,cubeSize/2,5)
    geo += newPoint(middle[0]+cubeSize, middle[1]-cubeSize, middle[2]+cubeSize,cubeSize/2,6)
    geo += newPoint(middle[0]+cubeSize, middle[1]+cubeSize, middle[2]+cubeSize,cubeSize/2,7)
    geo += newPoint(middle[0]-cubeSize, middle[1]+cubeSize, middle[2]+cubeSize,cubeSize/2,8)

    geo += newLine('p1','p2',1)
    geo += newLine('p2','p3',2)
    geo += newLine('p3','p4',3)
    geo += newLine('p4','p1',4)
    geo += newLine('p5','p6',5)
    geo += newLine('p6','p7',6)
    geo += newLine('p7','p8',7)
    geo += newLine('p8','p5',8)
    geo += newLine('p1','p5',9)
    geo += newLine('p2','p6',10)
    geo += newLine('p3','p7',11)
    geo += newLine('p4','p8',12)

    geo += "Line Loop(1) = {l1,l2,l3,l4};\nLine Loop(2) = {l5,l6,l7,l8};\nLine Loop(3) = {l1,l10,-l5,-l9};\nLine Loop(4) = {l2,l11,-l6,-l10};\nLine Loop(5) = {l3,l12,-l7,-l11};\nLine Loop(6) = {l4,l9,-l8,-l12};\n"

    geo += "Plane Surface(11) = {1};\nPlane Surface(12) = {2};\nPlane Surface(13) = {3};\nPlane Surface(14) = {4};\nPlane Surface(15) = {5};\nPlane Surface(16) = {6};\n"

    geo += "Surface Loop(1) = {11,13,14,15,16,12};\nVolume(11) = {1};\n"

    geo += "For t In {0:" + str(counter_lines-1) + "}\n   Line{t} In Volume{11};\nEndFor"

    # Cube generation .dmg
    dmg += "auto c = gmod::new_cube(gmod::Vector{" + str(minPoint[0]) + ", " + str(minPoint[1]) + ", " + str(minPoint[2]) + "},gmod::Vector{" + str(cubeSize) + ", 0, 0},gmod::Vector{0, " + str(cubeSize) + ", 0},gmod::Vector{0, 0, " + str(cubeSize) + "});\n"
    dmg += "gmod::add_to_group(g, c);\n"
    dmg += 'write_closure_to_geo(g, "neuron.geo");\nwrite_closure_to_dmg(g, "neuron.dmg");\n}'



    return [geo,dmg,txt]

def checkMinMax(a,mini,maxi):
    retMin = mini
    retMax = maxi
    if (a<mini):
        retMin = a
    if (a>maxi):
        retMax = a
    return [retMin,retMax]

def newPoint(x,y,z,g,i):
    return "p" + str(i) + " = newp;\nPoint(p" + str(i) + ") = {" + str(x) + ", " + str(y) + ", " + str(z) + ", " + str(g) + "};\n"

def newLine(p1,p2,i):
    return "l" + str(i) + " = newl;\nLine(l" + str(i) + ") = {" + str(p1) + "," + str(p2) + "};\n"
