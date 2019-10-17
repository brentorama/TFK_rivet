import maya.cmds
import re

def getMesh(verbose=False):

    mesh = {}
    if not (maya.cmds.pluginInfo("matrixNodes", q=True, l=True)):
        maya.cmds.loadPlugin( "matrixNodes" )
    input = maya.cmds.filterExpand(sm = 32)

    if input and len(input) >=2:  
        
        shapes = list(set(maya.cmds.listRelatives(input, p=True)))
        obs = maya.cmds.listRelatives(shapes, p=True)
        for one in obs:
            mesh[one] = {"shapes" : maya.cmds.listRelatives(obs, shapes=True),
            "input" : maya.cmds.filterExpand(sm = 32),
            "count" : len(input),
            "edgeMax" : maya.cmds.polyEvaluate(obs, e=True)}
        if verbose:
            print(mesh)
    else:
        print("bRivet requires at least 2 edges to be selected")
    return mesh


def createNodes(mesh, verbose=False, dryrun=False):

    count = mesh["count"]
    edgeMax = mesh["edgeMax"]
    doublets = zip(range(count-1),range(1, count))
    nodes = {"pointOnSurfaceInfo": {"name" : "pos", "node" : []},
            "loft": {"name":"loft", "node" : []},
            "fourByFourMatrix":{"name" : "mat", "node" : []},
            "locators" : [],
            "decomposeMatrix":{"name" : "dcp", "node" : []},
            "curveFromMeshEdge" : {"name" : "cFM", "node" : []}}
    i=1

    for pair in doublets:
        for k in nodes:
            if verbose:
                print (pair, k, i)
            if k is not "locators":
                name = "%s%02d" % (nodes[k]["name"], i)
                nodes[k]["node"].append(maya.cmds.createNode(k, name = name))
            if k is "pointOnSurfaceInfo":
                maya.cmds.setAttr("%s.turnOnPercentage" % nodes[k]["node"][-1], 1)
            if k is "loft":
                maya.cmds.setAttr("%s.degree" % nodes[k]["node"][-1], 1)
            if k is "curveFromMeshEdge":
                maya.cmds.setAttr("%s.edgeIndex[0]" % nodes[k]["node"][-1], pair[0])  
            if k is "locators":
                loc = "rivet%02d" % i
                maya.cmds.spaceLocator(name = loc)
                for uv in "UV":
                    maya.cmds.addAttr(loc, at="float2", ln=uv, dv=0.5)
                for one in range(2):
                    maya.cmds.addAttr(loc, at="short", ln ="edgeIndex%d" % one, min = 0, max = edgeMax, k = True, dv = pair[one])
                nodes[k].append({"name" : loc, "doublet" : pair})
        i+=1

    finalCfm = maya.cmds.createNode("curveFromMeshEdge", name = "%s%02d" % (nodes["curveFromMeshEdge"]["name"], i))
    maya.cmds.setAttr("%s.edgeIndex[0]" % finalCfm, doublets[-1][1])  
    nodes["curveFromMeshEdge"]["node"].append(finalCfm)

    return nodes

def connectNodes(nodes, mesh):
    pass


def brivet(dryrun=False, verbose=False):

    mesh = getMesh(verbose=False)

    if not len(mesh):
        if verbose:
            print("Error getting mesh")
        return

    pnt = ["normal", "tangentU.tangentU", "tangentV.tangentV", "position.position"]
    xyz = ["X","Y","Z"]
    uv = "UV"

    for one in mesh:

        count = one["count"]
        locs = []
        gpName = "rivet%02d_GP" % m
        if not maya.cmds.objExists(gpName)
            maya.cmds.group(em = True, name = gpName)

        nodes = createNodes(mesh[one])
        connectNodes(nodes, mesh)
        
        for one in [0,1]:    
 
            cA("%s.edgeIndex%d" % (loc[0],one), "%s.edgeIndex[0]" % ed)   
            cA("%s.worldMesh[0]" % shape[0] , "%s.inputMesh" % ed)
            cA("%s.outputCurve" % ed, "%s.inputCurve[%s]" % (var[1][1], one))

        print "ok%s"%m
    
        for UV in uv:
            cA("%s.UV.%s" % (loc[0], UV), "%s.parameter%s" % (var[0][1], UV))

        for m in range(4):
            for j in range(3):
                o = xyz[j]
                if m in [1,2]: 
                    o = o.lower()
                cA("%s.%s%s" %(var[0][1], pnt[m], o), "%s.in%s%s" % (var[2][1], m, j))
                
        cA("%s.outputSurface" % var[1][1], "%s.inputSurface" % var[0][1])
        cA("%s.output" % var[2][1], "%s.inputMatrix" % var[3][1])
        cA("%s.outputTranslate" % var[3][1], "%s.t" % gp)
        cA("%s.outputRotate" % var[3][1], "%s.r" % gp)

        locs.append(loc[0])
    
    maya.cmds.select(locs)
        
bRivet()