import maya.cmds as cmd
import re

def bRivet():

    input = cmd.filterExpand(sm = 32)
    if input and len(input) >=2:  
        ob = input[0].split('.')[0]
        edgeMax = cmd.polyEvaluate(ob, e=True)
        shape = cmds.listRelatives(ob, shapes=True)
        count = len(input)
        cmds.undoInfo( state=False )  
        try:
            bRivet_Build(input,ob,edgeMax,shape, count)
        except:
            cmd.warning('Something is not right')
        cmds.undoInfo( state=True ) 
    else:
        cmd.warning('bRivet requires at least 2 edges to be selected')

def bRivet_Build(input, ob, edgeMax, shape, count):
    
    cA = cmd.connectAttr
    sA = cmd.setAttr
    aA = cmd.addAttr
    cN = cmd.createNode
    var = [['pointOnSurfaceInfo','pos'],['loft','loft'],['fourByFourMatrix','mat'],['decomposeMatrix','dcp']]
    pnt = ['normal', 'tangentU.tangentU', 'tangentV.tangentV', 'position.position']
    xyz = ['X','Y','Z']
    uv = 'UV'        
    doublet = zip(range(count-1),range(1, count))
    locs = []
    
    for pair in doublet:

        for n in range(4):
            var[n][1] = cN(var[n][0], name = var[n][1])
            
        loc = cmd.spaceLocator(name = 'rivet')   
        sA('%s.turnOnPercentage' % var[0][1], 1)
        sA('%s.degree' % var[1][1], 1)
        aA(loc[0], at = 'float2', ln= uv) 
                    
        for one in [0,1]:    
            num = int(re.findall("\[(.*?)\]", input[pair[one]])[0])
            aA(loc[0], at = 'short' , ln = 'edgeIndex%d' % one, min = 0, max = edgeMax, k = True, dv = num)
            ed = cN('curveFromMeshEdge', name = 'cFM')
            sA('%s.edgeIndex[0]' % ed, num)   
            cA('%s.edgeIndex%d' % (loc[0],one), '%s.edgeIndex[0]' % ed)   
            cA('%s.worldMesh[0]' % shape[0] , '%s.inputMesh' % ed)
            cA('%s.outputCurve' % ed, '%s.inputCurve[%s]' % (var[1][1], one))
            aA(loc[0], at = 'float' , ln = uv[one], k = True, p= uv, min = 0, max = 1)   
    
        for UV in uv:
            cA('%s.UV.%s' % (loc[0], UV), '%s.parameter%s' % (var[0][1], UV))
            sA('%s.UV.%s' % (loc[0], UV), 0.5)        
                
        for i in range(4):
            for j in range(3):
                o =  xyz[j]
                if i in [1,2]: o = o.lower()
                cA('%s.%s%s' %(var[0][1], pnt[i], o), '%s.in%s%s' % (var[2][1], i, j))
                
        cA('%s.outputSurface' % var[1][1], '%s.inputSurface' % var[0][1])
        cA('%s.output' % var[2][1], '%s.inputMatrix' % var[3][1])
        cA('%s.outputTranslate' % var[3][1], '%s.t' % loc[0])
        cA('%s.outputRotate' % var[3][1], '%s.r' % loc[0])

        locs.append(loc[0])
    
    cmd.select(locs)
       
bRivet()