# DEC to FOL

## Authors
- Raghav Nauhria, IIT Madras, [LinkedIn](https://www.linkedin.com/in/raghavnauhria), [GitHub](https://github.com/raghavnauhria)  
- Nipam Basumatary, IIT Madras

## Prerequisites
- Install python 3.x

## Execution
```
python3 parivartan.py -i path_to_input_file -o path_to_output_file -p path_to_predicates_file
```

## Write your input file
Things to keep in mind:
- Newline is default de-limiter
- Everyline must be ended with a period, i.e. ".", as shown below
- Spacing must be as specified below

### 1. List of sorts (if required)
```
sort <AgentName1>.
sort <AgentName2>.
...
```

### 2. List of events and fluents
Event/fluent definitions and references must be consistent throughout.

```
event <EventName>.
event <EventName>(<AgentName1>,<AgentName2>).
fluent <FluentName>.
event <FluentName>(<AgentName3>,<AgentName4>).
...
```

### 3. List of agents
Agents can not inherited amongst each other, i.e. one agent can not be the instance of another
For single instance agents, follow the format same way as for the others.
```
<AgentName1> <AgentName1_instance1>.
<AgentName1> <AgentName1_instance2>.

<AgentName2> <AgentName2_instance1>.
<AgentName2> <AgentName2_instance2>.
...
```


### 4. List of time instances
"timeInstance" can not be an agent or an event, i.e. it is atomic

```
time <timeInstance1>.
time <timeInstance2>.
...
```

### 5. Additional resources (if required)
example, noninertial
```
noninertial <EventName>.
noninertial <EventName>(<AgentName1>,<AgentName2>).
...
```

### 6. Action descriptions
```
[event,time] <PredicateName>(<FluentName>,time).
[time] <PredicateName>(<EventName>,<FluentName>,time).
[fluent,time] <PredicateName>(<EventName>(<AgentName1>,<AgentName2>),fluent,time).
[fluent,time] <PredicateName>(<EventName>(<AgentName1_instance1>,<AgentName2>),fluent,time).
...
```

### 7. State constraint
arguments for fluents in state constraints are not supported yet.
```
[time] HoldsAt(<FluentName1>,time) <-> !HoldsAt(<FluentName2>,time).
[time] !HoldsAt(<FluentName1>,time) <-> HoldsAt(<FluentName2>,time).
```

### 8. Initial State
arguments for fluents are supported here.
```
HoldsAt(<FluentName>,<timeInstance>).
!HoldsAt(<FluentName>,<timeInstance>).
```

### 9. Sequence of Events
arguments for fluents are supported here.
```
Happens(<EventName>,<timeInstance>).
Happens(<EventName>(<AgentName1>,<AgentName2>),<timeInstance>).
Happens(<EventName>(<AgentName1_instance1>,<AgentName2>),<timeInstance>).
```