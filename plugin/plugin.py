#!/usr/bin/python

from lib.Addons.Plugin.Client.Interface import CInterface
from lib.Exceptions import *
import random

from condition import Condition
from activity import Activity

inf = float('inf')

class CCriticalPathFinder(object):
    
    def __init__(self, interface):
        
        self.interface = interface
        self.interface.StartAutocommit()
        self.adapter = interface.GetAdapter()
        self.guimanager = self.adapter.GetGuiManager()
        mainmenu = self.guimanager.GetMainMenu()
        mnuTools = mainmenu.AddMenuItem('mItemGraphTools', None, -1, 'Graph Tools')
        mnuTools = mnuTools.AddSubmenu()
        mnuTools.AddMenuItem('mItemCriticalPath', self.activity, 0, 'Find critical Path')
    
    def activity(self, path):
        try:
            project = self.interface.GetAdapter().GetProject()
            if project is None:
                self.guimanager.DisplayWarning("No project loaded")
                return
            
            metamodel = project.GetMetamodel()
            if metamodel.GetUri() != 'urn:umlfri.org:metamodel:graphTheory':
                self.guimanager.DisplayWarning('Not supported metamodel')
                return
            
            diagram = self.interface.GetAdapter().GetCurrentDiagram()
            if diagram is None or diagram.GetType() != 'Critical Path diagram':
                self.guimanager.DisplayWarning('Critical path not supported on current diagram')
                return
            
            conditionlist = {}
            activities = {}
            conditions = {}
            for e in diagram.GetElements():
                o = e.GetObject()
                t = o.GetType()
                if t == 'activity':
                    activities[e.GetId()] = Activity(e)
                
                elif t == 'condition':
                    activities[e.GetId()] = conditions[e.GetId()] = Condition(e)
                
                elif t == 'conditionList':
                    conditionlist.update(dict([
                        (str(item['name']), item['value'] == 'True')
                        for item in eval(o.GetValue('conditions'))
                    ]))
            
            for c in conditions.itervalues():
                c.SetConditions(conditionlist)
            
            
            for c in diagram.GetConnections():
                s, d = c.GetSource(), c.GetDestination()
                activities[s.GetId()].AddNext(c, activities[d.GetId()])
                activities[d.GetId()].AddPrev(c, activities[s.GetId()])
            
            
            #monotonne usporiadanie
            idx = 0
            beginners = [a for a in activities.itervalues() if a.SumPrev() == 0]
            
            while beginners:
                first = beginners.pop(0)
                first.SetIdx(idx)
                idx += 1
                for hop in first.NextHops():
                    hop.DecPrev()
                    if hop.SumPrev() == 0:
                        beginners.append(hop)
            
            for a in activities.itervalues():
                a.ref.GetObject().SetValue('index', str(a.idx))
                
            if idx < len(activities):
                self.guimanager.DisplayWarning('Cycle in graph')
                return
            
            #hladanie casov
            sort = sorted(activities.values(), lambda x,y: cmp(x.idx, y.idx))
            
            
            for n in activities.itervalues():
                if len(n.prev) == 0:
                    n.time[0] = [0, n.Duration()]
            for n in sort:
                n.SendNext()
            
            for n in activities.itervalues():
                if len(n.next) == 0:
                    n.time[1] = [n.time[0][0], n.time[0][1]]
            for n in reversed(sort):
                n.SendPrev()
                
            for a in activities.itervalues():
                o = a.ref.GetObject()
                if o.GetType() == 'activity':
                    o.SetValue('minstart', str(a.time[0][0]))
                    o.SetValue('minend', str(a.time[0][1]))
                    o.SetValue('maxstart', str(a.time[1][0]))
                    o.SetValue('maxend', str(a.time[1][1]))
                else:
                    o.SetValue('value', a.val)
                o.SetValue('critical', a.IsCritical())
                for c, n in a.next:
                    c.GetObject().SetValue('critical', a.IsCritical() and n.IsCritical() and a.time[0][1] == n.time[0][0])
            
            self.a = activities
            self.s = sort
            
        except PluginProjectNotLoaded:
            self.guimanager.DisplayWarning('Project is not loaded')
        except (KeyError, ), e:
            self.guimanager.DisplayWarning('Unknown condition called "%s"'%e.args)
        except:
            self.guimanager.DisplayWarning('Unkown error in plugin')

# selecting plugin main object
pluginMain = CCriticalPathFinder

if __name__ == '__main__':
    import sys
    interface = CInterface(int(sys.argv[1]))
    c = CCriticalPathFinder(interface)
    while 1:
        time.sleep(1.)
