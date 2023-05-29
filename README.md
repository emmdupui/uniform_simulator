# uniform_simulator
Event based simulator for uniform multiprocessor platforms.

## Implemented
- 6 scheduling algorithms
  - RM
  - EDF
  - AFD
  - FFD
  - EDF_FF_IS_DU
  - Level
- Experiments to analyse performances (**migrations**, **preemptions** and **feasibility rates**)

## Run
In order to run the experiments we must run the command:
```
python3 main.py -runId id --WF wf --tasks tasks --exp exp
```
- id is an int corresponding the run id which is used as a seed to generate task sets 
- wf is a bool (0 or 1) which corresponds to whether we enable waterfall migrations or not
- tasks is a string corresponding to the directory of the tasks which will be generated 
- exp is an int 
  - 0 : number of repetions before result stabilisation experiment
  - 1 : means and std result experiment 
