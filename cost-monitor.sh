#!/bin/bash

# Azure Cost Monitor and Auto-Shutdown Script
# Run this script periodically to monitor costs and shutdown VM if over budget

BUDGET_LIMIT=30.0
RESOURCE_GROUP="RG-SAMRUDHPRAKASH3084-9928"
VM_NAME="anomaly-detection-vm"
EMAIL="samrudhprakash3084@gmail.com"

echo "🔍 Checking Azure costs..."

# Get current month's costs (this is approximate)
CURRENT_COST=$(az monitor metrics list \
    --resource "/subscriptions/24d67073-9070-49be-9748-f0b68d3a8e1f/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Compute/virtualMachines/$VM_NAME" \
    --metric "Percentage CPU" \
    --query "value[0].timeseries[0].data[-1].average" \
    --output tsv 2>/dev/null)

# Since we can't easily get exact costs via CLI, let's use a simple estimation
# Based on VM runtime and pricing
VM_STATUS=$(az vm show --resource-group $RESOURCE_GROUP --name $VM_NAME --query powerState -o tsv)

if [ "$VM_STATUS" = "VM running" ]; then
    echo "⚡ VM is currently running"

    # Get VM creation time for rough cost calculation
    CREATED_TIME=$(az vm show --resource-group $RESOURCE_GROUP --name $VM_NAME --query timeCreated -o tsv)
    CREATED_TIMESTAMP=$(date -d "$CREATED_TIME" +%s)
    CURRENT_TIMESTAMP=$(date +%s)
    HOURS_RUNNING=$(( (CURRENT_TIMESTAMP - CREATED_TIMESTAMP) / 3600 ))

    # Estimate cost (Standard_B2s = ~$0.0089/hour)
    ESTIMATED_COST=$(echo "scale=2; $HOURS_RUNNING * 0.0089" | bc)

    echo "⏱️  Hours running: $HOURS_RUNNING"
    echo "💰 Estimated cost: \$$ESTIMATED_COST"

    if (( $(echo "$ESTIMATED_COST > $BUDGET_LIMIT" | bc -l) )); then
        echo "🚨 BUDGET EXCEEDED! Cost: \$$ESTIMATED_COST > Limit: \$$BUDGET_LIMIT"

        # Send email alert
        echo "Budget exceeded! VM will be shutdown. Cost: \$$ESTIMATED_COST" | mail -s "Azure Budget Alert" $EMAIL 2>/dev/null || echo "Email notification failed"

        # Shutdown VM
        echo "🛑 Shutting down VM..."
        az vm stop --resource-group $RESOURCE_GROUP --name $VM_NAME

        echo "✅ VM shutdown completed"
        echo "💰 Final cost: ~\$$ESTIMATED_COST"
    else
        REMAINING=$(echo "scale=2; $BUDGET_LIMIT - $ESTIMATED_COST" | bc)
        echo "✅ Within budget. Remaining: \$$REMAINING"
    fi
else
    echo "🛑 VM is currently stopped"
fi

echo "📊 Cost monitoring completed"
