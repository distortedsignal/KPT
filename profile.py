import time
import subprocess
import argparse
import sys

# Set up command line flags
parser = argparse.ArgumentParser(description='Type of Profiling you want to exectute')
parser.add_argument('-p', '--port', type=int, metavar='', required=True)
parser.add_argument('-H', '--heap', action='store_true', help="Add heap profile")
parser.add_argument('-b', '--blocking', action='store_true', help="Add blocking profile")
parser.add_argument('-m', '--mutex', action='store_true', help="Add mutex profile")
parser.add_argument('-c', '--cpu', default=0, type=int, help="Add cpu profile for x seconds")
parser.add_argument('-t', '--tracing', default=0, type=int, help="Add tracing profile for x seconds")
args = parser.parse_args()

# Check that only one profile was requested
sum = 0
for arg in vars(args):
  attr = getattr(args, arg)
  if isinstance(attr, bool):
    if attr == True:
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

# Find the name of the kubedirector pod
# First find starting index
index = output.find('kubedirector')
# Kubedirector pod not found
if index == -1:
  print('Kubedirector pod could not be found')
  sys.exit()
podName = ''
# Starting with index, add each character from kubedirector pod name until we reach a space 
while output[index] != ' ':
  podName += output[index]
  index += 1
print("Pod name: " + podName) 

# Get port num from command line args
portNum = str(args.port)

# Forward localhost of pod to outside port of user's preference
pfProcess = subprocess.Popen(["kubectl", "port-forward", podName, "6060"])

# Need to sleep for a short time period so port-forward operation can run. Otherwise, connection fails
time.sleep(.2)

# Parse out profile type from command line args
if args.heap:
  profileType = 'heap'
elif args.block:
  profileType = 'block'
elif args.mutex:
  profileType = 'mutex'
elif args.cpu:
  profileType = 'profile?seconds' + str(args.c)
elif args.tracing:
  profileType = 'trace?seconds' + str(args.t)

# Use go tool to generate profile
baseStr = ["go", "tool", "pprof", "http://localhost:" + portNum + "/debug/pprof/" + profileType]

# Command to issue to pprof upon startup
str_var = "exit"
# Encode to bytes so it's readable by system
profProcess = subprocess.run(baseStr, input= str_var.encode('utf-8'))

# Kill port-forward process so we can do this again without manually killing
subprocess.run(["echo", "Killing port forward process..."])
subprocess.run(["kill", str(pfPid)])
