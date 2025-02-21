import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Load environent variables
load_dotenv("C:/Users/anayebia/variables.env")
       
# Access environment variables

subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID")
client_secret= os.getenv("AZURE CLIENT_SECRET")
client_id=os.getenv("AZURE_CLIENT_ID")
tenant_id=os.getenv("AZURE_TENANT_ID")
resource_group="ComputeOptimizationRG"
vm_name="VM1"


# Authenticate with Azure

credential= DefaultAzureCredential()

#Initiate Clients

compute_client = ComputeManagementClient(credential,subscription_id)
monitor_client_metrics = MonitorManagementClient(credential, subscription_id)

# Fetch VM details
print("Fetching VM details...")
vms= compute_client.virtual_machines.list_all()
for vm in vms:
      print(f"VM Name:{vm.name}, Location:{vm.location}, Size: {vm.hardware_profile.vm_size}")

# Fetch CPU metrics for a VM

print( "\nFetching CPU metrics...")
metrics_data = monitor_client_metrics.metrics.list(
    resource_uri = "/subscriptions/d531f8b9-d42d-43d1-b30c-2346361594e7/resourceGroups/ComputeOptimizationRG/providers/Microsoft.Compute/virtualMachines/VM1", # The full Azure Resource ID for the monitored resource
    timespan="PT1H",  # Last 1 hour
    interval="PT15M",
    metricnames="Percentage CPU",
    aggregation="Average"
)

for metrics in metrics_data.value:
    for timeseries in metrics.timeseries:
        for data in timeseries.data:
            print(f"Timestamp:{data.time_stamp}, CPU Usage: {data.average}%")


import sqlite3
#Connect to SQLite Database
conn= sqlite3.connect("azure_data.db")
cursor=conn.cursor()

#Create Tables
cursor.execute("""
      CREATE TABLE IF NOT EXISTS vms(
      id INTEGER PRIMARY KEY,
      name TEXT,
      location TEXT,
      size TEXT

)
""")

# Insert Vm details into the table
for vm in vms:
      cursor.execute("INSERT INTO vms(name, location, size) VALUES (?,?,?)", (vm.name, vm.location, vm.hardware_profile.vm_size))

# Commit and Close the connection
conn.commit()
conn.close()

#Extract Metric Data
timestamps=[]
cpu_usage=[]
for metric in metrics_data.value:
      for timeseries in metric.timeseries:
            for data in timeseries.data:
                  timestamps.append(data.time_stamp)
                  cpu_usage.append(data.average)

#Create a DataFrame

data= pd.DataFrame({
      "Timestamp": timestamps,
      "CPU Usage": cpu_usage
})


plt.figure(figsize=(10,6))
plt.plot(timestamps, cpu_usage, marker='o', linestyle='-', color='b')
plt.title("CPU Usage Over Time")
plt.xlabel("Time")
plt.ylabel("CPU Usage (%)")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()



