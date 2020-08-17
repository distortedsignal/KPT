# KPT - Kubernetes Profiling Tool

This is a simple python script to ease the process of profiling Go applications that are contained within a Kubernetes pod/cluster. Currently only functional for kubedirector or hpecp-agent applications, or other applications if set up correctly and contained within a given pod

## Command Line Arguments
- --localport, -l (int): Local port to be used in kubectl port-forward command. This is the port you wish to access profiling endpoints from. 
- --remoteport, -r (int): Remote port to be used in kubectl port-forward command. This is the port you start your server on in your code
- --port, -p (int): Shorthand for when localport=remoteport. This option overrides local and remote port options if all are set  
Regarding Ports:  Since the commands are run for the user, it should be no trouble to use this easier -p option and use the same port numbers. However some ports may already be in use, so we have specific options for local and remote ports as well. 
- --pod (str): Designates the pod that you wish to profile within
- --app, -a (str): Designates the application that you wish to instrument (Options include: kubedirector, kd , hpecp-agent, hpecpagent, agent)
- --heap, -H (bool): Enables heap profiling
- --block, -b (bool): Enable goroutine blocking profiling
- --mutex, -m (bool): Enables mutex profiling
- --cpu, -c (int): Enables cpu profiling for a user-determined number of seconds.
- --tracing, -t (int): Enables execution tracing for a user-determined number of seconds

CLA Note:
- When profiling for a certain amount of time (cpu and tracing), the tool will start the profiling, but it's up to the user to perform actions they want to be profiled on a separate terminal window. The tool will not provide the user with a terminal to perform commands. It will simply wait until the time frame has elapsed and then show the user the results.
- Analyzing a trace will require Google chrome. If using a headless machine, the trace will still be created but the script will obviously fail to launch the browser.

## Usage
 MAJOR NOTE: This tool is designed for Go programs running within a container, which itself is running in a Kubernetes pod. Your main function must have the following block of code:
```
go func() {
	log.Println(http.ListenAndServe("localhost:6060", nil))
}()
```

If you do not have this, you may receive an error message with something along the lines of: "Connect: Connection Refused. Failed to fetch source profiles."
You may also choose your own port number to set up the server on, 6060 is merely an example. See the --port command line argument
Lastly, you must be able to run kubectl commands on whatever machine you are currently using, as you need to be able to access cluster nodes and pods for this to work. 

Steps:
- All current pods will be checked, and the first kubedirector pod will be identified. (Tool only currently works for KubeDirector)
- The tool will execute a "kubectl port-forward" command on this pod to redirect it's localhost to the outer port that you've specified in the CLA. 
- The tool will execute a "go tool pprof <profile-endpoint>" command to creating the profile (or start it, if cpu or tracing) 
- The tool will immediately exit out of the pprof CLI in order to clean up the kubectl process, but it will reactivate it using the file path immediately after

## Common Error
If you get an error message that says something about a port already being used, you must manually kill the port-forward process on your machine. There are certain special cases where this may occur. Start by retrieving the processes on your machine:
```
    $ netstat -tulpn
```
Then locate the PID of the program "Kubectl", and execute the following command:
```
    $ kill <kubectl-pid>
```
