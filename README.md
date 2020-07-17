# KPT - Kubernetes Profiling Tool

This is a simple python script to ease the process of profiling Go applications that are contained within a Kubernetes pod/cluster. Currently only functional for kubedirector or hpecp-agent applications, or other applications if set up correctly and contained within a given pod

## Command Line Arguments
- --port, -p (int): Desginates the port you want to use to access profiling endpoints. 
- --pod (str): Designates the pod that you wish to profile within
- --app, -a (str): Designates the application that you wish to instrument (Options include: kubedirector, kd , hpecp-agent, hpecpagent, agent)
- --heap, -H (bool): Enables heap profiling
- --block, -b (bool): Enable goroutine blocking profiling
- --mutex, -m (bool): Enables mutex profiling
- --cpu, -c (int): Enables cpu profiling for a user-determined number of seconds.
- --tracing, -t (int): Enables execution tracing for a user-determined number of seconds

CLA Notes:
- When profiling for a certain amount of time (cpu and tracing), the tool will start the profiling, but it's up to the user to perform actions they want to be profiled on a separate terminal window. The tool will not provide the user with a terminal to perform commands. It will simply wait until the time frame has elapsed and then show the user the results.
- You may only select one type of profiling. So you should have exactly two command line arguments: Port and a Profile Type.

## Usage
 MAJOR NOTE: This tool is designed for Go programs running within a container, which itself is running in a Kubernetes pod. Your main function must have the following block of code:
```
go func() {
	log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```
You may, however, choose your own port number. Otherwise, if this is not your situation, the tool will not work.
Also, you must be able to run kubectl commands on whatever machine you are currently using, as you need to be able to access cluster nodes and pods for this to work. 

Steps:
- All current pods will be checked, and the first kubedirector pod will be identified. (Tool only currently works for KubeDirector)
- The tool will execute a "kubectl port-forward" command on this pod to redirect it's localhost to the outer port that you've specified in the CLA. 
- The tool will execute a "go tool pprof <profile-endpoint>" command to creating the profile (or start it, if cpu or tracing) 
- After the profile is created, the pprof CLI is activated. However, the tool will immediately exit this CLI to properly execute clean-up operations. The output tells the user the location of the profile, and from there it is a simple command to get back to that CLI:
``` 
    go tool pprof <profile-file>
```


## Common Error
If you get an error message that says something about a port already being used, you must manually kill the port-forward process on your machine. There are certain special cases where this may occur. Start by retrieving the processes on your machine:
```
    $ netstat -tulpn
```
Then locate the PID of the program "Kubectl", and execute the following command:
```
    $ kill <kubectl-pid>
```
