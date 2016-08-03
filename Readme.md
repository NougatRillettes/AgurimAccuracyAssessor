#Agurim Accuracy Assessor

This repo contains various scripts to assess the quality of agurim. The different folders are as follow:

- `OutputComparer` contains comparer.py, which takes a ground-truth and a tested output and run the munkres algorithm for the transportation problem on them
- `PlotMaker` contains the scripts to do the two different kind of curves:
    -  `curve.py` is used to compare several algortihm measurements.
	  -  `scatter.py` is used to plot a single algorithm measurement

##Typical workflow

Let's say we have the ouput of three algorithm: `agurim.agr`, `aguri2.agr` and `both.agr`, as well as a ground-truth `truth.agr`.

To do the measurements:

```
./comparer.py truth.agr agurim.agr > agurim.meas
./comparer.py truth.agr aguri2.agr > aguri2.meas
./comparer.py truth.agr both.agr > both.meas
```

Then multiple plots are possible, for example (the `-s` option instructs the script to display the plot an not only save it):

```
./scatter.py -s agurim.meas 'This is an optional subtitle'
./curve.py -s agurim.meas aguri2.meas both.meas 
```

##More info

Each of this script has a `-h` option that should be helpful.
