# KPT - Kubernetes Profiling Tool

This is a simple python script to ease the process of profiling Go applications that are contained within a Kubernetes pod/cluster. It takes two command line flags, one for the port you wish to access the profiling data on, and one for the type of profiling. 

## Command Line Arguments
- --port, -p (int): Desginates the port you want to use to access profiling endpoints. 
- --heap, -H (bool): Enables heap profiling
- --block, -b (bool): Enable goroutine blocking profiling
- --mutex, -m (bool): Enables mutex profiling
- --cpu, -c (int): Enables cpu profiling for a user-determined number of seconds.
- --tracing, -t (int): Enables execution tracing for a user-determined number of seconds

Note: When profiling for a certain amount of time (cpu and tracing), the tool will start the profiling, but it's up to the user to perform actions they want to be profiled on a separate terminal window. The tool will not provide the user with a terminal to perform commands. It will simply wait until the time frame has elapsed and then show the user the results.
## Common Error
If you get an error message that says something about a port already being used, you must manually kill the port-forward process on your machine. There are certain special cases where this may occur. Start by retrieving the processes on your machine:
```
    $ netstat -tulpn
```
Then locate the PID of the program "Kubectl", and execute the following command:
```
    $ kill <kubectl-pid>
```