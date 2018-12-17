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

from enum import Enum
from graphviz import Digraph

import inspect

''' 
Every node has a unique type in a map graph and every type defined a   
different style like colour and shape.

root node: Alway be the map's root, can be any kinds of objects
cls: class
obj: instance
func: function
str: string
tuple: typle
dict: dictionary
list: list
number: int float bool and complex
clsfunc: class function
method: object method
abstract: abstract
generator: generator
traceback: traceback
descriptor: method and data descriptor
other: all not includes in list upon
'''
NodeType = Enum('NodeType', 'root cls obj func str number \
                tuple list dict clsfunc method abstract generator \
                traceback descriptor other')

def isnumber(obj):
    '''Return true if obj is int, float, bool or complex'''
    
    if isinstance(obj, int) \
       or isinstance(obj, float) \
       or isinstance(obj, bool) \
       or isinstance(obj, complex):
            return True
    return False

def isdescriptor(obj):
    if inspect.ismethoddescriptor(obj) or inspect.isdatadescriptor(obj):
        return True
    return False   

def isother(obj):
    for i in type_isdict:
        if i == NodeType.other:
            continue
        if type_isdict[i](obj):
            return False

    if inspect.isbuiltin(obj) or inspect.ismodule(obj):
        return False    

    return True

type_isdict = { NodeType.cls      : inspect.isclass,
                #NoteType.obj has function below  with different parameters
                NodeType.func     : inspect.isfunction,
                NodeType.str     : lambda obj: isinstance(obj, str),
                NodeType.number  : isnumber,
                NodeType.tuple   : lambda obj: isinstance(obj, tuple),
                NodeType.list    : lambda obj: isinstance(obj, list),
                NodeType.dict    : lambda obj: isinstance(obj, dict),

                NodeType.clsfunc   : inspect.isfunction,
                NodeType.method    : inspect.ismethod,
                NodeType.abstract  : inspect.isabstract,
                NodeType.generator : inspect.isgenerator,
                NodeType.traceback : inspect.istraceback,
                NodeType.descriptor: isdescriptor,
                NodeType.other: isother,
              }

class ObjMap():
    def __init__(self, obj):
        self.root_node = obj
        
        ''' get root node module name obj belongs to '''
        try:
            module = inspect.getmodule(obj)
            self.root_module = module.__name__
        except:
            pass
    
        ''' get root node name itself '''
        try:
            self.root_node_name = obj.__name__
        except:
            ''' style like <sample.A object at 0xb70f418c> '''
            name = str(obj)
            if name.startswith('<'):
                name = name.split()[0]
                name = name[1:] + ".instance"
            self.root_node_name = name
        
        # get a type str like 1 -> 'int'
        typestr = str(type(obj))
        typestr = typestr.split("'")[1]
        if typestr == "type": 
            typestr = "class"  # class is more usual

        self.root_type = typestr

    def isin_root_module(self, clsinfo):
        ''' clsinfo is in the same module as this class '''
        
        ''' if root node don't have module info, be true arbitrary'''
        if len(self.root_module) == 0: 
            return True

        try:
            if clsinfo.__module__ != self.root_module:
                return False
        except:
            pass
        
        return True

    def __objs_predicate(self, obj, predicate):
        ''' generate all nodes with predicate '''
        objs = []
        for name,type in inspect.getmembers(obj, predicate):
            if(self.isin_root_module(getattr(obj, name))):
                objs.append(getattr(obj, name))

        return objs
    
    def __obj_nodes_predicate(self, obj, predicate):
        ''' generate all nodes with predicate '''
        nodes = []
        for name,type in inspect.getmembers(obj, predicate):
            if(self.isin_root_module(getattr(obj, name))):
                nodes.append(name)

        return nodes

    def __obj_edges_predicate(self, obj, predicate):
        ''' generate all edges from obj to nodes with predicate '''
        nodes = self.__obj_nodes_predicate(obj, predicate)
        if len(nodes) == 0:
            return []

        edges = []
        for i in nodes:
            edges.append([obj.__name__, i])
    
        return edges
    
    def root_nodes(self, obj):
        ''' create root node, a node is as ['namestr'] '''
        name = self.root_node_name
        if len(self.root_module) and not inspect.ismodule(obj):
            name = self.root_module + '.' + self.root_node_name

        return [name]

    def class_nodes(self, obj):
        nodes = self.__obj_nodes_predicate(obj, type_isdict[NodeType.cls])
        return nodes
    
    def func_nodes(self, obj):
        return self.__obj_nodes_predicate(obj, type_isdict[NodeType.func])
    
    def tuple_nodes(self, obj):
        return self.__obj_nodes_predicate(obj, type_isdict[NodeType.tuple])

    def list_nodes(self, obj):
        return self.__obj_nodes_predicate(obj, type_isdict[NodeType.list])

    def dict_nodes(self, obj):
        return self.__obj_nodes_predicate(obj, type_isdict[NodeType.dict])

    def str_nodes(self, obj):
        return self.__obj_nodes_predicate(obj, type_isdict[NodeType.str])
    
    def number_nodes(self, obj):
        return self.__obj_nodes_predicate(obj, type_isdict[NodeType.number])
    
    def abstract_nodes(self, obj):
        return self.__obj_nodes_predicate(obj, type_isdict[NodeType.abstract])
    
    def generator_nodes(self, obj):
        return self.__obj_nodes_predicate(obj, type_isdict[NodeType.generator])
    
    def traceback_nodes(self, obj):
        return self.__obj_nodes_predicate(obj, type_isdict[NodeType.traceback])
    
    @staticmethod
    def isprivate_name(name):
        return name.startswith("__")

    def descriptor_nodes(self, obj):
        nodes = []
        for name,type in inspect.getmembers(obj, type_isdict[NodeType.descriptor]):
            if not self.isprivate_name(name):
                nodes.append(name)
    
        return nodes 

    @staticmethod
    def __iscls_instance(obj, classes, name):        
        var = getattr(obj, name)
        for i in classes:
            if isinstance(var, i):
                return True
        return False

    def obj_classes(self, obj):
        return self.__objs_predicate(obj, type_isdict[NodeType.cls])
    
    def obj_nodes(self, obj):
        nodes = []
        
        for name,typ in inspect.getmembers(obj):
            if self.isprivate_name(name):
                continue

            if self.__iscls_instance(obj, self.obj_classes(obj), name):
               nodes.append(name)

        return nodes
    
    def other_nodes(self, obj):
        nodes = []

        for name,typ in inspect.getmembers(obj, type_isdict[NodeType.other]):
            if name.startswith('__'):
                continue
            ''' exclude objs '''
            if not self.__iscls_instance(obj, self.obj_classes(obj), name):
               nodes.append(name)
    
        return nodes

    # trim all methods if name same as the cls
    def objmethod_nodes(self, obj):
        nodes = []
        for name,type in inspect.getmembers(obj, type_isdict[NodeType.method]):
            nodes.append(name)
    
        return nodes
    
    def objmethod_filter_nodes(self, obj):
        clsnodes = []
        nodes = []
        for name,type in inspect.getmembers(obj.__class__, type_isdict[NodeType.func]):
            clsnodes.append(name)
        
        for name,type in inspect.getmembers(obj, type_isdict[NodeType.method]):
            if name not in clsnodes:
                nodes.append(name)
    
        return nodes
    
    ''' html table node styles '''
    method_style = {"title" : "methods", "align" : "left", "color" : "#bebada",
                    "get_nodes" : objmethod_nodes}
    function_style = {"title" : "functions", "align" : "left", "color" : "#bebada",
                            "get_nodes" : func_nodes}
    incls_method_style = method_style.copy()
    incls_method_style['get_nodes'] = objmethod_filter_nodes
    
    hnode_styles = {
        # * means this style will be updated dynamically
        NodeType.root:     {"title" : "*",  "align" : "center", "color" : "#8dd3c7",
                            "get_nodes" : root_nodes},
        NodeType.cls:      {"title" : "classes", "align" : "left", "color" : "SandyBrown",
                            "get_nodes" : class_nodes,
                             NodeType.clsfunc:  {"title" : "functions", "align" : "left",  
                                                 "color" : "#bebada",
                                                 "get_nodes" : func_nodes},
                             NodeType.descriptor:{"title" : "descriptors", "align" : "left",  
                                                 "color" : "YellowGreen",
                                                 "get_nodes" : descriptor_nodes},
                           },
        NodeType.obj:      {"title" : "instances", "align" : "left", "color" : "SandyBrown",
                            "get_nodes" : obj_nodes,
                             NodeType.method: incls_method_style,
                             NodeType.func : function_style,
                           },
        NodeType.method:   method_style,
        NodeType.func:     function_style,
        NodeType.str:      {"title" : "strings", "align" : "left",  "color" : "Gainsboro",
                            "get_nodes" : str_nodes},
        NodeType.number:   {"title" : "numbers", "align" : "left", "color" : "Gainsboro",
                            "get_nodes" : number_nodes}, 
                            
        NodeType.tuple:    {"title" : "tuples", "align" : "left",  "color" : "BurlyWood",
                            "get_nodes" : tuple_nodes},
        NodeType.list:     {"title" : "lists", "align" : "left",  "color" : "BurlyWood",
                            "get_nodes" : list_nodes},
        NodeType.dict:     {"title" : "dicts", "align" : "left",  "color" : "BurlyWood",
                            "get_nodes" : dict_nodes},

        NodeType.abstract: {"title" : "abstracts", "align" : "left", "color" : "Salmon",
                            "get_nodes" : abstract_nodes},                        
        NodeType.generator:{"title" : "generators", "align" : "left", "color" : "Salmon",
                            "get_nodes" : generator_nodes},                        
    
        NodeType.traceback:{"title" : "tracebacks", "align" : "left", "color" : "red",
                            "get_nodes" : traceback_nodes},
        NodeType.other:    {"title" : "others", "align" : "left", "color" : "Gainsboro",
                            "get_nodes" : other_nodes},
      }

    # 'root.' prefix avoid attrnames conflict, so the name is for node
    def root_type_title_update(self, obj):
        self.hnode_styles[NodeType.root]['title'] = '.'.join(["root", self.root_type])
        
    # remove it while show it in table
    @staticmethod
    def root_type_title_remove_prefix(title):
        if title.startswith("root."):
            return title[title.find('.') + 1:]
        return title
    
    @classmethod
    def label_htab_create(cls, nodes, title, align="center", color="SandyBrown"):
        tab_header = '''<<table border="0" cellborder="1" cellspacing="0">\n'''
        tab_tail = "</table>>\n"
        
        title = cls.root_type_title_remove_prefix(title)
        th = '\t<tr><td bgcolor="%s" style="rounded"><b><i>%s</i></b></td></tr>\n'\
             % (color, title)
    
        trs = ""
        for i in nodes:
            trs += '''\t<tr><td port="%s" align="%s">%s</td></tr>\n''' % (i, align,i)
        return tab_header + th + trs + tab_tail

    def dot_add_htab_node(self, dot, obj, nodetype, style=None, title=None):
        if style == None:
            style = self.hnode_styles[nodetype]

        get_nodes_func = style['get_nodes']
        if not get_nodes_func:
            print("can't get nodes function for", nodetype)
            return False

        if nodetype == NodeType.root: # update the root's title
            self.root_type_title_update(obj)

        if title == None:
            title = style['title']
            
        nodes = get_nodes_func(self, obj)
        if len(nodes):
            lab = self.label_htab_create(nodes, title, style['align'], 
                                         style['color'])
            dot.node(title, label=lab, shape="plaintext")
            for i in NodeType:
                if not style.__contains__(i):
                    continue
                for node in nodes:
                    subtitle = node + "." + style[i]['title']
                    if self.dot_add_htab_node(dot, getattr(obj, node), i, 
                                              style[i], subtitle):
                        dot.edge(':'.join([title, node]), subtitle, 
                                 color=style[i]['color'])
            return True
        return False

    def dot_add_obj_nodes(self, dot, obj):
        handled_nodes = []
        for i in self.hnode_styles:
            if self.dot_add_htab_node(dot, obj, i):
                handled_nodes.append(i)

        for i in handled_nodes:
            if i == NodeType.root:
                continue
            dot.edge(self.hnode_styles[NodeType.root]['title'], 
                     self.hnode_styles[i]['title'],
                     color=self.hnode_styles[i]['color'])

        def clsobj_relation_edges(self, inobj):
            edges = []
            objnodes = self.obj_nodes(inobj)
            clsnodes = self.class_nodes(inobj)
        
            for obj in objnodes:
                for cls in clsnodes:
                    if isinstance(getattr(inobj, obj), getattr(inobj, cls)):
                        edges.append([cls, obj])
            return edges
    
        # at last add instances and cls relationship
        edges = clsobj_relation_edges(self, obj)
        if not len(edges):
            return
        
        dot.attr('edge', style="dashed", color=self.hnode_styles[NodeType.obj]['color'])
        objtitle = self.hnode_styles[NodeType.obj]['title']
        clstitle = self.hnode_styles[NodeType.cls]['title']
        for i in edges:
            dot.edge(':'.join([clstitle, i[0]]), ':'.join([objtitle, i[1]]))
    
    # Rank directions: "TB", "LR", "BT", "RL"
    # splines: "spline", "ortho", "polyline", "curved", "line"
    # reference to' https://graphviz.gitlab.io/_pages/doc/info/attrs.html#d:splines'
    # 'polyline' is better when there're many lines between nodes
    def objmap_create(self, filename="obj.gv", format="png", rankdir="TB", splines="spline"):
        dot = Digraph('structs', node_attr={'shape': 'record'})

        dot.attr(rankdir=rankdir)
        dot.attr(splines=splines)
        dot.attr(compound='true')
        #dot.attr(concentrate='true')

        self.dot_add_obj_nodes(dot, self.root_node)
        dot.render(filename, format=format, view=False)
        dot.save()

class StackMap():
    @staticmethod
    def label_stacktab_create(stack, align="left", color="SandyBrown"):
        tab_header = '''<<table border="0" cellborder="1" cellspacing="0">\n'''
        tab_tail = "</table>>\n"
        index_num = 0
        th = '\t<tr><td bgcolor="%s"><b><i>%s</i></b></td>'\
             '<td bgcolor="%s"><b><i>%s</i></b></td>'\
             '<td bgcolor="%s"><b><i>%s</i></b></td>'\
             '<td bgcolor="%s"><b><i>%s</i></b></td>'\
             '<td bgcolor="%s"><b><i>%s</i></b></td>'\
             '</tr>\n'  % (color, "no", color, "file", color, "lineno", \
                           color, "function", color, "index")
    
        trs = ""
        for i in stack:
            frame,filename,lineno,funcname,lines,index = i
            
            if filename.startswith("./"):
                filename = filename[2:]
            funcname = funcname.strip('<>')
            
            tr = '\t<tr bgcolor="%s">'\
                 '<td align="%s">%s</td>'\
                 '<td align="%s">%s</td>'\
                 '<td align="%s">%s</td>'\
                 '<td align="%s">%s</td>'\
                 '<td align="%s">%s</td>'\
                 '</tr>\n'  % (color, align, index_num, align, filename, align, \
                               lineno, align, funcname, align, index)
            index_num += 1
            trs += tr
     
        return tab_header + th + trs + tab_tail
    
    # Rank directions: "TB", "LR", "BT", "RL"
    @classmethod
    def draw_stack(cls, stack, filename="stack.gv", format="png", rankdir="TB"):
        dot = Digraph('structs', node_attr={'shape': 'record'})
        dot.attr(rankdir=rankdir)
        lab = cls.label_stacktab_create(stack)
        dot.node(filename, label=lab, shape="plaintext")
    
        dot.render(filename, format=format, view=False)
        dot.save()

def test():
    import sample.sample
    objmap = ObjMap(sample.sample)
    objmap.objmap_create()
    StackMap.draw_stack(inspect.stack())

if __name__ == "__main__":
    test()