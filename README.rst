nesting
=======

This module is a Python port of the [`nest` operator](https://github.com/mbostock/d3/wiki/Arrays#wiki-d3_nest) from Mike Bostock's [d3.js](http://d3js.org).


Nest allows elements in an array to be grouped into a hierarchical tree structure;
think of it like the GROUP BY operator in SQL, except you can have multiple levels of
grouping, and the resulting output is a tree rather than a flat table. The levels in
the tree are specified by key functions. The leaf nodes of the tree can be sorted by
value, while the internal nodes can be sorted by key. An optional rollup function will
collapse the elements in each leaf node using a summary function. The nest operator
(the object returned by d3.nest) is reusable, and does not retain any references to the
data that is nested.

For example, consider the following tabular data structure of Barley yields, from
various sites in Minnesota during 1931-2:

>>> yields = [
    {"yield": 27.00, "variety": "Manchuria", "year": 1931, "site": "University Farm"},
    {"yield": 48.87, "variety": "Manchuria", "year": 1931, "site": "Waseca"},
    {"yield": 27.43, "variety": "Manchuria", "year": 1931, "site": "Morris"}, 
    {"yield": 43.07, "variety": "Glabron",   "year": 1931, "site": "University Farm"},
    {"yield": 55.20, "variety": "Glabron",   "year": 1931, "site": "Waseca"},
    {"yield": 16.18, "variety": "Glabron",   "year": 1932, "site": "University Farm"},
]


To facilitate visualization, it may be useful to nest the elements first by year, and then by variety, as follows:

>>> from nesting import Nest
>>> (Nest()
...     .key( lambda d: d['year'] )
...     .key( lambda d: d['variety'] )
...     .entries(yields))


Or more concisely:

>>> (Nest()
...     .key('year')
...     .key('variety')
...     .entries(yields))


...as both the `key` and `prop` functions will interpret non-callables as they key to look up.

This returns a nested array. Each element of the outer array is a key-values pair, listing the values for each distinct key::

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

--

This port is open-source, freely licensed under the [MIT License](http://dsc.mit-license.org).
