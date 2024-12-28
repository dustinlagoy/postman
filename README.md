# Postman

A basic library and CLI to solve Meigu Guan's postman problem on a network of real paths.

## Background

I wanted to find the easiest route to traverse a series of local trails, making sure to traverse each trail at least once. Turns out this is the well studied problem Meigu Guan originally described.

Taking into account both trail distance and elevation gain in determining the easiest route is a variant of this problem known as the windy postman problem. As shown in [Meigu Guan 1984](https://doi.org/10.1016%2F0166-218X%2884%2990089-1) this has a polynomial bounded solution when every cycle in a network has the same weight when traversed forwards and backwards. For a real trail network this will always be true.

This repository contains code for reading and preprocessing trail network data (which turned out to take most of my time), solving the windy postman problem to return a minimum length tour, and saving the result as a GPX file for use in the field.

[momepy](http://momepy.org) handles most of the preprocessing and [networkx](https://networkx.org) does most of the graph solving. I had to update one algorithm from networkx (still a WIP) to take into account edges that do not all have the same weight.

## Usage

Assuming you have a vector file (that geopandas can read) of trails (including elevations) that have already been split at every intersection (I did this by hand with QGIS) you can run something like:

```sh
postman /path/to/input_file.shp -s out.gpx
```

to generate the minimal postman route and save the result in `out.gpx`.

There are also some plotting capabilities, mostly useful to check the validity of the loaded and preprocessed graph, that can be accessed via:

```sh
postman /path/to/input_file.shp -p
```
