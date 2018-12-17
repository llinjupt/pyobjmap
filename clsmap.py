# -*- coding: utf-8 -*-

"""
Tools for drawing Python class inherit and MRO graphs with graphviz.

Copyright (c) 2017-2018 Red Liu <lli_njupt@163.com>

Released under the MIT licence.
"""
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from graphviz import Digraph

''' picker on X11 color different from last time '''
class CPicker():

    ''' Brewer color schemes refer to https://graphviz.org/doc/info/colors.html '''
    ylgn9 = ('#ffffe5', '#f7fcb9', '#d9f0a3', '#addd8e', '#78c679', '#41ab5d', 
             '#238443', '#006837', '#004529')
    ylorbr9 =('#ffffe5', '#fff7bc', '#fee391', '#fec44f', '#fe9929', '#ec7014', 
              '#cc4c02', '#993404', '#662506')
    set312 = ('#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462', 
              '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd', '#ccebc5', '#ffed6f')
    rdylgn9 = ('#d73027', '#f46d43', '#fdae61', '#fee08b', '#ffffbf', '#d9ef8b', 
               '#a6d96a', '#66bd63', '#1a9850')
    
    __reds = ('IndianRed', 'LightCoral', 'Salmon', 'DarkSalmon', 
              'LightSalmon', 'Crimson', 'Red', 'FireBrick')
    __greens =('MediumSeaGreen', 'SeaGreen', 'ForestGreen', 'Green', 
              'DarkGreen', 'YellowGreen', 'OliveDrab', 'DarkOliveGreen')
    __browns = ('Cornsilk', 'BlanchedAlmond', 'Bisque', 'NavajoWhite', 'Wheat',
              'BurlyWood', 'Tan', 'RosyBrown', 'SandyBrown', 'Goldenrod', 
              'DarkGoldenrod', 'Peru', 'Chocolate', 'SaddleBrown', 'Sienna', 
              'Brown', 'Maroon')

    __greys = ('Gainsboro', 'LightGrey', 'Gray',
               'DimGray', 'LightSlateGray', 'SlateGray', 'DarkSlateGray')

    cnames = {"red" : __reds, 
              "green" : __greens, 
              "brown": __browns, 
              "grey": __greys,
              "set312": set312,
              "ylgn9": ylgn9,
              "ylorbr9" : ylorbr9,
              "rdylgn9" : rdylgn9,
              }
    colors = ((len(set312), set312),
              (len(__browns), __browns),
              (len(__greens), __greens), 
              (len(__greys), __greys),
              (len(__reds), __reds),)

    rotate_index = {"cindex": 0, "index" : 0}
    order_index = 0
    total_len = 0
    colors_num = len(colors)
    
    for i in range(colors_num):
        total_len += colors[i][0]

    @classmethod
    def __single_picker(cls, cname):
        if not cls.cnames.__contains__(cname):
            return
        
        index_name = cname + "_index"
        if not cls.cnames.__contains__(index_name):
            cls.cnames[index_name] = 0
        
        index = cls.cnames[index_name]
        cls.cnames[index_name] += 1
        return cls.cnames[cname][index % len(cls.cnames[cname])]

    ''' support method: order, rotate, red, green, brown ,set39 and grey'''
    @classmethod
    def picker(cls, method="set312"):
        color = "white"
        if method == "rotate":
            cindex = cls.rotate_index["cindex"] % len(cls.colors)
            index = cls.rotate_index["index"] % cls.colors[cindex][0]
            color = cls.colors[cindex][1][index]
            cls.rotate_index["cindex"] += 1
            if cls.rotate_index["cindex"] % cls.colors_num == 0:
                cls.rotate_index["index"] += 1
        elif method == "order":
            index = cls.order_index % cls.total_len
            for i in range(cls.colors_num):
                if index - cls.colors[i][0] >= 0:
                    index -= cls.colors[i][0]
                else:
                    color = cls.colors[i][1][index]
                    break
            cls.order_index += 1
        else:
            newcolor = cls.__single_picker(method)
            if newcolor:
                color = newcolor
        return color

class ClsMap():
    def __init__(self):
        pass

    @staticmethod
    def __is_cls(clsinfo):
        try:
            issubclass(clsinfo, object)
            return True
        except:
            print("Err:", clsinfo, "is not a subclass of object.")
        return False

    @staticmethod
    def __cls_name(clsinfo):
        try: 
            cls_name = clsinfo.__name__
        except:
            print("Warn:", clsinfo, "has no name, set default as NoN.")
            cls_name = "NoN"
        return cls_name

    @staticmethod
    def __module_name(clsinfo):
        return clsinfo.__module__
    
    @staticmethod
    def __node_module_name(node):
        rindex = node.rfind('.')
        return node[0:rindex]
    
    @staticmethod
    def __node_last_name(node):
        rindex = node.rfind('.')
        return node[rindex + 1:]

    @staticmethod
    def __edges_rm_module_name(edges):
        newedges = []
        for i in edges:
            newedges.append([ClsMap.__node_last_name(i[0]), 
                             ClsMap.__node_last_name(i[1])])

        return newedges 
    
    @staticmethod
    def __edges_in_same_module(edges):
        for i in edges:
            if ClsMap.__node_module_name(i[1]) != ClsMap.__node_module_name(i[0]):
                return False

        return True
    
    # may have duplicate paths
    @staticmethod
    def __inherit_edges_get(clsinfo):
        edges = []

        for i in (clsinfo.__bases__):
            edges.append([clsinfo.__name__, i.__name__])
            if i != object:
                subedges = ClsMap.__inherit_edges_get(i)
                if len(subedges):
                    edges.extend(subedges)
        
        return edges
    
    # remove duplicate paths
    @staticmethod
    def __edges_dup_remove(edges):
        new_edges = []
        for i in edges:
            if i in new_edges:
                continue
            new_edges.append(i)

        return new_edges
    
    @classmethod
    def inherit_edges(cls, clsinfo):
        if not ClsMap.__is_cls(clsinfo):
            return []
        edges = ClsMap.__inherit_edges_get(clsinfo)
        return ClsMap.__edges_dup_remove(edges)
    
    @classmethod
    def mro_edges(cls, clsinfo):
        if not ClsMap.__is_cls(clsinfo):
            return []
        
        edges = []
        start = clsinfo.__mro__[0].__name__
    
        for i in clsinfo.__mro__[1:]:
            edges.append([start, i.__name__])
            start = i.__name__
    
        return edges
    
    @classmethod
    def subclasses_edges(cls, clsinfo):
        def __subclasses_edges(cls, clsinfo):
            edges = []
            
            try:
                subclasses = clsinfo.__subclasses__()
            except TypeError:
                subclasses = clsinfo.__subclasses__(type)
    
            for i in subclasses:
                if clsinfo == i:
                    print("Warn:", clsinfo, "looped itself!")
                    continue
    
                edges.append([i.__module__ + "." + i.__name__, \
                              clsinfo.__module__ + "." + clsinfo.__name__])
                subedges = cls.subclasses_edges(i)
                if len(subedges):
                    edges.extend(subedges)
    
            return edges
        
        return ClsMap.__edges_dup_remove(__subclasses_edges(cls, clsinfo))

    @classmethod
    def draw_mro(cls, clsinfo, filename="mro.gv", format="png"):
        if not ClsMap.__is_cls(clsinfo):
            return

        mro_edges = cls.mro_edges(clsinfo)
        if not len(mro_edges):
            return

        clsinfo_name = ClsMap.__cls_name(clsinfo)
        dot = Digraph(comment='Class %s MRO map' % clsinfo_name)
        # Rank directions: "TB", "LR", "BT", "RL"
        dot.attr(rankdir='LR')
        dot.edge_attr.update(color='red')
        dot.node(mro_edges[0][0], style="filled")
        dot.edges(mro_edges)
        dot.render(filename, format=format, view=False)

    @classmethod
    def draw_map(cls, clsinfo, filename="map.gv", format="png", with_mro=False):
        if not ClsMap.__is_cls(clsinfo):
            return

        clsinfo_name = ClsMap.__cls_name(clsinfo)
        dot = Digraph(comment='Class %s inherit relationship map' % clsinfo_name)

        if clsinfo == object:
            edges = [["object", "NUL"]]
        else:
            edges = cls.inherit_edges(clsinfo)

        dot.node(edges[0][0], style="filled")
        if not with_mro:
            dot.edges(edges)
        else:
            mro_edges = cls.mro_edges(clsinfo)
            for i in edges:
                if i in mro_edges:
                    mro_edges.remove(i)
                    dot.edge(i[0], i[1], color='red')
                else:
                    dot.edge(i[0], i[1])
            for i in mro_edges:
                dot.edge(i[0], i[1], color='red')

        dot.render(filename, format=format, view=False)
        
    @classmethod
    def draw_subclasses(cls, clsinfo, filename="subclasses.gv", format="png"):
        if not ClsMap.__is_cls(clsinfo):
            return

        edges = cls.subclasses_edges(clsinfo)
        if not len(edges):
            return
        
        multiple_modules = True
        if ClsMap.__edges_in_same_module(edges):
            edges = ClsMap.__edges_rm_module_name(edges)
            multiple_modules = False
        clsinfo_name = ClsMap.__cls_name(clsinfo)
        dot = Digraph(comment='Class %s subclasses tree' % clsinfo_name)
        dot.attr(rankdir='LR')
        dot.attr(splines="polyline")
        dot.node(edges[0][1], style="filled")

        if multiple_modules: # add node color for different modules
            color_plate = {}
            for edge in edges:
                for node in edge:
                    module_name = ClsMap.__node_module_name(node)
                    if not color_plate.__contains__(module_name):
                        color_plate[module_name] = CPicker.picker()

                    dot.node(node, style='filled', fillcolor=color_plate[module_name])
 
        dot.edges(edges)
        dot.render(filename, format=format, view=False)

def test():
    class A():
        def f0(self):
            print('A f0')
    
        def f1(self):
            print('A f1')
    
    class B(object):
        def f0(self):
            print('B f0')
    
        def f1(self):
            print('B f1')
    
    class C(B):
        def f0(self):
            print('C f0')
    
    class D(A, B):
        def f1(self):
            print('D f1')

    class E(D, B):
        pass

    class F(E, C, B):
        pass

    print("F Inherit edges:", ClsMap.inherit_edges(F))
    print("F MRO edges:", ClsMap.mro_edges(F))
    print("A Subclasses edges:", ClsMap.subclasses_edges(A))

    ClsMap.draw_map(F, filename="map") 
    ClsMap.draw_map(F, filename="map_withmro", with_mro=True) 
    ClsMap.draw_mro(F)
    ClsMap.draw_subclasses(BaseException, filename="BaseException")

if __name__ == '__main__':
    test()
