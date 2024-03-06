import os
import proactive
import getpass

from dotenv import load_dotenv
load_dotenv()

print("Logging on proactive-server...")
proactive_url = os.getenv("PROACTIVE_URL")
if not proactive_url:
    proactive_url = input("Server (default: https://try.activeeon.com:8443): ")
if proactive_url == "":
    proactive_url  = "https://try.activeeon.com:8443"
if not proactive_url.startswith("http"):
    proactive_url  = "https://"+proactive_url+".activeeon.com:8443"

print("Connecting on: " + proactive_url)
gateway = proactive.ProActiveGateway(base_url=proactive_url)

username = os.getenv("PROACTIVE_USERNAME")
password = os.getenv("PROACTIVE_PASSWORD")
if not (username and password):
    username = input("Login: ")
    password = getpass.getpass(prompt="Password: ")
gateway.connect(username, password)
assert gateway.isConnected() is True
print("Connected")

try:
    print("Creating a proactive job...")
    proactive_job = gateway.createJob()
    proactive_job.setJobName("SimpleJob")

    print("Creating a proactive task #1...")
    proactive_task_1 = gateway.createPythonTask()
    proactive_task_1.setTaskName("SimplePythonTask1")
    proactive_task_1.setTaskImplementation("""print("Hello from " + variables.get("PA_TASK_NAME"))""")
    proactive_task_1.addGenericInformation("PYTHON_COMMAND", "python3")

    print("Adding a selection script to the proactive task #1...")
    proactive_task_1_selection_script = gateway.createSelectionScript(language="groovy")
    proactive_task_1_selection_script.setImplementationFromFile("../scripts/check_node_source_name.groovy")
    proactive_task_1.setSelectionScript(proactive_task_1_selection_script)
    proactive_job.addVariable("NODE_SOURCE_NAME", "Server-Static-Nodes")

    print("Adding proactive tasks to the proactive job...")
    proactive_job.addTask(proactive_task_1)

    print("Submitting the job to the proactive scheduler...")
    job_id = gateway.submitJob(proactive_job, debug=False)
    print("job_id: " + str(job_id))

    print("Getting job output...")
    job_result = gateway.getJobResult(job_id)
    print(job_result)

finally:
    print("Disconnecting")
    gateway.disconnect()
    print("Disconnected")
    gateway.terminate()
    print("Finished")
