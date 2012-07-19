#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Original `nest` operator from d3.js, by Mike Bostock
# https://github.com/mbostock/d3/wiki/Arrays#wiki-d3_nest
#
# Ported to Python by David Schoonover <dsc@less.ly>

__version__ = '0.1.0'
VERSION = tuple(map(int, __version__.split('.')))


from collections import defaultdict, namedtuple, OrderedDict
from operator import itemgetter, attrgetter

Entry = namedtuple('Entry', 'key values')



class Nest(object):
    """ Nest allows elements in an array to be grouped into a hierarchical tree structure;
        think of it like the GROUP BY operator in SQL, except you can have multiple levels of
        grouping, and the resulting output is a tree rather than a flat table. The levels in
        the tree are specified by key functions. The leaf nodes of the tree can be sorted by
        value, while the internal nodes can be sorted by key. An optional rollup function will
        collapse the elements in each leaf node using a summary function. The nest operator
        (the object returned by d3.nest) is reusable, and does not retain any references to the
        data that is nested.
        
        For example, consider the following tabular data structure of Barley yields, from
        various sites in Minnesota during 1931-2:
        
            yields = [
                {"yield": 27.00, "variety": "Manchuria", "year": 1931, "site": "University Farm"},
                {"yield": 48.87, "variety": "Manchuria", "year": 1931, "site": "Waseca"},
                {"yield": 27.43, "variety": "Manchuria", "year": 1931, "site": "Morris"}, 
                {"yield": 43.07, "variety": "Glabron",   "year": 1931, "site": "University Farm"},
                {"yield": 55.20, "variety": "Glabron",   "year": 1931, "site": "Waseca"},
                {"yield": 16.18, "variety": "Glabron",   "year": 1932, "site": "University Farm"},
            ]
        
        To facilitate visualization, it may be useful to nest the elements first by year, and then by variety, as follows:
        
            Nest()
                .key( lambda d: d['year'] )
                .key( lambda d: d['variety'] )
                .entries(yields)
        
        Or more concisely:
        
            Nest()
                .key('year')
                .key('variety')
                .entries(yields)
        
        ...as both the `key` and `prop` functions will interpret non-callables as they key to look up.
        
        This returns a nested array. Each element of the outer array is a key-values pair, listing the values for each distinct key:
        
            [   {"key": 1931, "values": [
                    {"key": "Manchuria", "values": [
                        {"yield": 27.00, "variety": "Manchuria", "year": 1931, "site": "University Farm"},
                        {"yield": 48.87, "variety": "Manchuria", "year": 1931, "site": "Waseca"},
                        {"yield": 27.43, "variety": "Manchuria", "year": 1931, "site": "Morris"}, ]},
                    {"key": "Glabron", "values": [
                        {"yield": 43.07, "variety": "Glabron", "year": 1931, "site": "University Farm"},
                        {"yield": 55.20, "variety": "Glabron", "year": 1931, "site": "Waseca"}, ]}, 
                ]},
                {"key": 1932, "values": [
                    {"key": "Glabron", "values": [
                        {"yield": 16.18, "variety": "Glabron", "year": 1932, "site": "University Farm"}, ]},
                ]},
            ]
        
        The nested form allows easy iteration and generation of hierarchical structures in SVG or HTML.
    """
    
    _keys       = None
    _sortKeys   = None
    _sortValues = None
    _rollup     = None
    
    
    def __init__(self):
        """ Creates a new nest operator. The set of keys is initially empty. If the map
            or entries operator is invoked before any key functions are registered, the
            nest operator simply returns the input array.
        """
        self._keys       = []
        self._sortKeys   = []
    
    
    def key(self, fn):
        """ Registers a new key function. The key function will be invoked for each
            element in the input array, and must return a string identifier that is used to
            assign the element to its group. As most often the key function is just a
            simple accessor, this fuction also accepts a non-callable, which will be converted
            into a function that simply performs a dictionary lookup via `operator.itemgetter`
            (constrast this with `prop()`, which simply uses attribute lookup via
            `operator.attrgetter`).
            
            Each time a key is registered, it is appended to the end of an internal keys
            array, and the resulting map or entries will have an additional hierarchy
            level. There is not currently a facility to remove or query the registered
            keys. The most-recently registered key is referred to as the current key in
            subsequent methods.
        """
        if not callable(fn):
            fn = itemgetter(fn)
        self._keys.append(fn)
        self._sortKeys.append({})
        return self
    
    
    def prop(self, fn):
        """ Registers a new key function. The key function will be invoked for each
            element in the input array, and must return a string identifier that is used to
            assign the element to its group. As most often the key function is just a
            simple accessor, this fuction also accepts a non-callable, which will be converted
            into a function that simply performs an attribute lookup via `operator.attrgetter`
            (constrast this with `key()`, which simply uses a dictionary lookup via
            `operator.itemgetter`).
            
            Each time a key is registered, it is appended to the end of an internal keys
            array, and the resulting map or entries will have an additional hierarchy
            level. There is not currently a facility to remove or query the registered
            keys. The most-recently registered key is referred to as the current key in
            subsequent methods.
        """
        if not callable(fn):
            fn = attrgetter(fn)
        self._keys.append(fn)
        self._sortKeys.append({})
        return self
    
    
    def sortKeys(self, cmp=None, key=None, reverse=False):
        """ Specifies the order for the most-recently specified key.
        """
        self._sortKeys[-1] = dict(cmp=cmp, key=key, reverse=reverse)
        return self
    
    
    def sortValues(self, cmp=None, key=None, reverse=False):
        """ Specifies the order for leaf values; applies to both maps and entries array.
        """
        self._sortValues = dict(cmp=cmp, key=key, reverse=reverse)
        return self
    
    
    def rollup(self, fn):
        """ Specifies a rollup function to be applied on each group of leaf elements.
            The return value of the rollup function will replace the array of leaf values
            in either the associative array returned by the map operator, or the values
            attribute of each entry returned by the entries operator.
        """
        self._rollup = fn
        return self
    
    
    def map(self, data, depth=0):
        """ Applies the nest operator to the specified array, returning an array of
            key-values entries. Each entry in the returned array corresponds to a distinct
            key value returned by the first key function. The entry value depends on the
            number of registered key functions: if there is an additional key, the value is
            another nested array of entries; otherwise, the value is the array of elements
            filtered from the input array that have the given key value.
        """
        if depth >= len(self._keys):
            if self._rollup:     return self._rollup(data)
            if self._sortValues: return sorted(data, **self._sortValues)
            return data
        
        values = defaultdict(list)
        it = data.iteritems() if isinstance(data, dict) else enumerate(data)
        for i, v in it:
            k = self._keys[depth](v)
            values[k].append(v)
        
        keys = values.keys()
        if self._sortKeys[depth]:
            keys = sorted(keys, **self._sortKeys[depth])
        
        return OrderedDict( (k, self.map(values.get(k), depth+1)) for k in keys )
    
    
    def _entries(self, data, depth=0):
        if depth >= len(self._keys):
            return data
        
        values = [ Entry(k, self._entries(v, depth+1)) for k, v in data.iteritems() ]
        
        keySort = self._sortKeys[depth]
        if keySort:
            # Remove `cmp` if it exists, wrapping it to pluck the key from the entry-tuple
            propCmp = keySort.pop('cmp', cmp)
            # Then apply the sort using the rest of the specified settings
            # def sorter(a,b):
            #     ret = propCmp(a['key'], b['key'])
            #     sign = '<' if ret < 0 else ('>' if ret > 0 else '=')
            #     print '%s %s %s' % (a['key'], sign, b['key'])
            #     return ret
            # values = sorted(values, cmp=sorter, **keySort)
            values = sorted(values, cmp=lambda a, b: propCmp(a['key'], b['key']), **keySort)
        
        return values
    
    
    def entries(self, data, depth=0):
        """ Applies the nest operator to the specified array, returning an associative
            array. Each Entry (a named tuple with the fields 'key' and 'values') in the
            returned associative array corresponds to a distinct key-value pair
            returned by the first key-function. The entry value depends on the number
            of registered key functions: if there is an additional key, the value is
            another nested associative array; otherwise, the value is the array of
            elements filtered from the input array that have the given key value.
        """
        return self._entries(self.map(data))
    
    def __len__(self):
        return len(self._keys)
    

