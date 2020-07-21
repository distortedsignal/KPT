import time
import subprocess
import argparse
import sys

# Set up command line flags
parser = argparse.ArgumentParser(description='Type of Profiling you want to exectute')
parser.add_argument('-p', '--port', type=int, required=True, help="Port you wish to access profiling endpoints from")
parser.add_argument('--pod', type=str, required=False, help="Pod you wish to profile within")
parser.add_argument('-H', '--heap', action='store_true', default=False, help="Add heap profile")
parser.add_argument('-b', '--block', action='store_true', default=False, help="Add blocking profile")
parser.add_argument('-m', '--mutex', action='store_true', default=False, help="Add mutex profile")
parser.add_argument('-c', '--cpu', default=0, type=int, help="Add cpu profile for x seconds")
parser.add_argument('-t', '--tracing', default=0, type=int, help="Add tracing profile for x seconds")
parser.add_argument('-a', '--app', type=str, required=False, help="Application you wish to instrument. Acceptable tags include: kubedirector, kd, hpecp-agent, hpecpagent, agent")
args = parser.parse_args()

# Check that exactly one profile was requested
sum = 0
for arg in vars(args):
  attr = getattr(args, arg)
  if isinstance(attr, bool):
    if attr == True:
      sum += 1
if args.cpu != 0:
    sum += 1
if args.tracing != 0:
    sum += 1
if sum != 1:
  print("Error: Need to have exactly one profiling flag set")
  sys.exit()

# Get pods, check kubectl installed
kV = subprocess.run("kubectl get po", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
output = kV.stdout.decode('ascii')
error = kV.stderr.decode('ascii')
if kV.stdout:
  print("Command success. Output:")
  print(output)
if kV.stderr:
  print("Error occurred. Error:")
  print(error)
  sys.exit()

# If we're not given the pod name, check if we're given an application. If we're not, exit and ask for an app/pod
if not (args.pod):
  if (args.app == 'kd' or args.app == 'kubedirector'):
    app = "kubedirector"
  elif (args.app == 'hpecp-agent' or args.app == 'agent' or args.app == 'hpecpagent'):
    app = "hpecp-agent"
  else:
    print("Application unrecognized or missing. Please provide a valid application or pod name")
    sys.exit()

  # Formulate pod name based off application name
  # Find starting index
  index = output.find(app)
  # App's pod not found
  if index == -1:
    print('Pod could not be found. Make sure you have an hpecp-agent or kubedirector pod active.')
    sys.exit()
  podName = ''
  # Starting with index, add each character from app's pod name until we reach a space (the end) 
  while output[index] != ' ':
    podName += output[index]
    index += 1
else:
  # Pod name was provided, just use that
  podName = args.pod

# Check that valid pod was found
err = output.find(podName)
if err == -1:
  print("Pod could not be found") 
  sys.exit()
print("Pod name: " + podName) 

# Get port num from command line args
portNum = str(args.port)

# Forward localhost of pod to outside port of user's preference
pfProcess = subprocess.Popen(["kubectl", "port-forward", podName, portNum])

# Need to sleep for a short time period so port-forward operation can run. Otherwise, connection fails (try to find way to not hardcode this, wait() or something) 
time.sleep(.2)

# Parse out profile type from command line args
if args.heap:
  profileType = 'heap'
elif args.block:
  profileType = 'block'
elif args.mutex:
  profileType = 'mutex'
elif args.cpu:
  profileType = 'profile?seconds' + str(args.cpu)
elif args.tracing:
  profileType = 'trace?seconds' + str(args.tracing)

# Use go tool to generate profile
baseStr = ["go", "tool", "pprof", "http://localhost:" + portNum + "/debug/pprof/" + profileType]

# Command to issue to pprof upon startup
str_var = "exit"

# Encode to bytes so it's readable by system
profProcess = subprocess.run(baseStr, stderr=subprocess.PIPE, stdout=subprocess.PIPE, input= str_var.encode('utf-8'))

# Find file path within stderr
error = profProcess.stderr.decode('ascii')
initialInd = error.find("Saved profile in")
pathInd = initialInd + 17
path = ''
while error[pathInd] != ' ':
    path += error[pathInd]
    pathInd += 1
print("Profile Path: " + path)

# Kill port-forward process so we can do this again without manually killing
subprocess.run(["echo", "Killing kubectl process..."])
subprocess.run(["kill", str(pfProcess.pid)])

# Access profile for user
runStr = "go tool pprof " + path
subprocess.run(runStr, shell=True)
