from plotly import colors
from rdkit import Chem
from rdkit.Chem import Draw, rdDepictor, rdFMCS, TemplateAlign
from rdkit.Chem.Draw import rdMolDraw2D
from svgutils import transform as sg

newcolors = []
c = [colors.hex_to_rgb(c) for c in colors.cyclical.mrybm]
#c = [colors.unlabel_rgb(c) for c in colors.sequential.Bluyl]

for i, e in enumerate(c[8:14]):
    newcolors.append(e)
    newcolors.append(colors.find_intermediate_color(e, c[i+9], 0.5))
newcolors = [ colors.unconvert_from_RGB_255(c) for c in newcolors ]
newcolorsH = []
# c = [colors.unlabel_rgb(c) for c in colors.sequential.Peach]

for i, e in enumerate(c[:6]):
    newcolorsH.append(e)
    newcolorsH.append(colors.find_intermediate_color(e, c[i+1], 0.5))
newcolorsH = [ colors.unconvert_from_RGB_255(c) for c in newcolorsH ]

def drawPerturbation(m1, m2, pairs, target='', n1='', n2='', text=''):
    d2d = rdMolDraw2D.MolDraw2DSVG(600,300,300,300)
    drawoptions = d2d.drawOptions()
    drawoptions.padding = 0.15
    drawoptions.prepareMolsBeforeDrawing = True
#     drawoptions.addAtomIndices = True
#     drawoptions.atomsLabels = True
#     d2d.SetDrawOptions(drawoptions)
#     drawoptions.centreMoleculesBeforeDrawing = False
    # Generate 2D Depictions
    mcs = rdFMCS.FindMCS([m1,m2], 
                         timeout=10) # find maximum common substructure (MCS)
    pattern = Chem.MolFromSmarts(mcs.smartsString) # generate mol with MCS
    match = m1.GetSubstructMatch(pattern) # get substruct match of MCS with first mol
    conf = m1.GetConformer(0) # get first molecule's conformer

    cnf = Chem.Conformer(len(match)) # generate a conformer for pattern
    [ cnf.SetAtomPosition(i, conf.GetAtomPosition(j)) for i, j in enumerate(match) ] # set pattern's atom position to first mol's atom positions
    pattern.AddConformer(cnf) # add conformer to pattern
    
    Chem.rdDepictor.GenerateDepictionMatching3DStructure(pattern, pattern) # generate depict of pattern matching 3D struct
    TemplateAlign.AlignMolToTemplate2D(m1,pattern) # generate depict for m1 aligned to pattern
    TemplateAlign.AlignMolToTemplate2D(m2,pattern) # generate depict for m2 aligned to pattern

    specialHighlight = []
    for i, p in enumerate(pairs):
        a1 = m1.GetAtomWithIdx(int(p[0]))
        a2 = m2.GetAtomWithIdx(int(p[1]))
        sameElement = a1.GetSymbol() == a2.GetSymbol()
        bothAromatic = a1.GetIsAromatic() and a2.GetIsAromatic()
        bothNotAromatic = not a1.GetIsAromatic() and not a2.GetIsAromatic()
        sameHybridization = a1.GetHybridization() == a2.GetHybridization()
        specialHighlight.append(not sameElement or not sameHybridization or not (bothAromatic or bothNotAromatic))
    
    highlightAtoms = [[int(p[0]) for p in pairs],
                      [int(p[1]) for p in pairs]]
    highlightAtomColors = [{int(p[0]): newcolorsH[i%len(newcolorsH)] if specialHighlight[i]  else newcolors[i%len(newcolors)] for i, p in enumerate(pairs)},
                           {int(p[1]): newcolorsH[i%len(newcolorsH)] if specialHighlight[i]  else newcolors[i%len(newcolors)] for i, p in enumerate(pairs)}]
    highlightAtomRadii = [{int(p[0]): .5 if specialHighlight[i]  else .33 for i, p in enumerate(pairs)},
                           {int(p[1]): .5 if specialHighlight[i]  else .33 for i, p in enumerate(pairs)}]
    
#     for atom in m1.GetAtoms():
#         atom.SetProp('atomLabel',str(atom.GetIdx()))
#     for atom in m2.GetAtoms():
#         atom.SetProp('atomLabel',str(atom.GetIdx()))        
    d2d.DrawMolecules([m1, m2],  
                      highlightAtoms=highlightAtoms, 
                      highlightAtomColors=highlightAtomColors, 
                      highlightAtomRadii=highlightAtomRadii, 
                      highlightBonds=[[],[]])

#     conf = m2.GetConformer(0)
#     crds=np.array([list(conf.GetAtomPosition(i)) for i in range(m2.GetNumAtoms())])
#     xrange = np.max(crds[:,0]) - np.min(crds[:,0])
#     yrange = np.max(crds[:,1]) - np.min(crds[:,1])
#     textx = -xrange*0.7
#     texty = yrange*0.7
# #d2d.SetOffset(0,0)
#     drawoptions.setSymbolColour((1,1,1))
#     d2d.SetFontSize(d2d.FontSize()*1.5)
#     d2d.DrawString(f'{target}', Point2D(textx, texty))
#     d2d.DrawString(f'{n1}->{n2}', Point2D(textx, texty-.75))
#     print(list(d2d.Offset()))
#     print(list(d2d.GetDrawCoords(Point2D(np.min(crds[:,0]), np.max(crds[:,1])))))
    d2d.FinishDrawing()
    s = d2d.GetDrawingText()
#     s = s.replace('svg:','')
    fig = sg.fromstring(s)
    
    label = sg.TextElement(300, 20, f'{target}: {n1} -> {n2}', size=20, 
                       font='sans-serif', anchor='middle', color='black')
    label2 = sg.TextElement(300, 35, f'{text}', size=15, 
                       font='sans-serif', anchor='middle', color='black')
    label3 = sg.TextElement(150, 285, f'{n1}', size=15, 
                       font='sans-serif', anchor='middle', color='black')
    label4 = sg.TextElement(450, 285, f'{n2}', size=15, 
                       font='sans-serif', anchor='middle', color='black')
    fig.append(label) 
    fig.append(label2) 
    fig.append(label3)
    fig.append(label4)
    return fig.to_str().decode("utf-8") 
