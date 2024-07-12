#!/bin/bash

# Create the main category rules YAML
cat <<EOL > category_rules.yaml
categories:
  - Food & Dining:
      - Groceries:
          rules: groceries_rules.yaml
      - Restaurants:
          rules: restaurants_rules.yaml
      - Coffee:
          rules: coffee_rules.yaml
      - Takeout:
          rules: takeout_rules.yaml
  - Accommodation & Utilities:
      - Utilities:
          - Electricity:
              rules: electricity_rules.yaml
          - Water:
              rules: water_rules.yaml
          - Gas:
              rules: gas_rules.yaml
      - Accommodation:
          rules: accommodation_rules.yaml
  - Money Transfers:
      rules: money_transfers_rules.yaml
  - Cash Withdrawal:
      rules: cash_withdrawal_rules.yaml
  - Transportation:
      - Fuel:
          rules: fuel_rules.yaml
      - Taxi:
          rules: taxi_rules.yaml
      - Travel Tickets:
          rules: travel_tickets_rules.yaml
      - Public Transportation:
          rules: public_transportation_rules.yaml
      - Vehicle Maintenance:
          rules: vehicle_maintenance_rules.yaml
      - Car Payments:
          rules: car_payments_rules.yaml
  - Healthcare:
      - Medical Bills:
          rules: medical_bills_rules.yaml
      - Health Insurance:
          rules: health_insurance_rules.yaml
      - Medications:
          rules: medications_rules.yaml
  - Shopping:
      - Clothes:
          rules: clothes_rules.yaml
      - Technology Items:
          rules: technology_items_rules.yaml
  - Personal Care:
      - Personal Grooming:
          rules: personal_grooming_rules.yaml
      - Fitness:
          rules: fitness_rules.yaml
  - Entertainment:
      - Movies:
          rules: movies_rules.yaml
      - Concerts:
          rules: concerts_rules.yaml
  - Subscriptions:
      rules: subscriptions_rules.yaml
  - Business & Services:
      - Cloud Server Payments:
          rules: cloud_server_payments_rules.yaml
  - Miscellaneous:
      rules: miscellaneous_rules.yaml
EOL

# Function to create rule YAML files
create_rule_yaml() {
  local filename=$1
  cat <<EOL > $filename
keywords: []
EOL
}

# Create all rule YAML files with a placeholder for keywords
create_rule_yaml groceries_rules.yaml
create_rule_yaml restaurants_rules.yaml
create_rule_yaml coffee_rules.yaml
create_rule_yaml takeout_rules.yaml
create_rule_yaml electricity_rules.yaml
create_rule_yaml water_rules.yaml
create_rule_yaml gas_rules.yaml
create_rule_yaml accommodation_rules.yaml
create_rule_yaml money_transfers_rules.yaml
create_rule_yaml cash_withdrawal_rules.yaml
create_rule_yaml fuel_rules.yaml
create_rule_yaml taxi_rules.yaml
create_rule_yaml travel_tickets_rules.yaml
create_rule_yaml public_transportation_rules.yaml
create_rule_yaml vehicle_maintenance_rules.yaml
create_rule_yaml car_payments_rules.yaml
create_rule_yaml medical_bills_rules.yaml
create_rule_yaml health_insurance_rules.yaml
create_rule_yaml medications_rules.yaml
create_rule_yaml clothes_rules.yaml
create_rule_yaml technology_items_rules.yaml
create_rule_yaml personal_grooming_rules.yaml
create_rule_yaml fitness_rules.yaml
create_rule_yaml movies_rules.yaml
create_rule_yaml concerts_rules.yaml
create_rule_yaml subscriptions_rules.yaml
create_rule_yaml cloud_server_payments_rules.yaml
create_rule_yaml miscellaneous_rules.yaml

echo "All YAML files have been created successfully."
