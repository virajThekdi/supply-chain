"""
Supply Chain Control Tower - Data Generation Script

Purpose:
    - Generate daily CSV files for production, shipments, inventory, suppliers, and quality
    - Simulate real-world scenarios (delays, defects, machine failures)
    - Maintain data relationships and constraints
    - Append data daily while preserving historical data

Usage:
    python scripts/generate_daily_data.py              # Generate for today
    python scripts/generate_daily_data.py --date 2026-04-05  # Generate for specific date
    python scripts/generate_daily_data.py --backfill 30      # Generate last 30 days
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import uuid
import argparse
from pathlib import Path
import json
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'RAW_DATA_PATH': 'data/raw',
    'PROCESSED_DATA_PATH': 'data/processed',
    'PLANTS': ['PLANT_US_01', 'PLANT_EU_01', 'PLANT_APAC_01'],
    'PRODUCTS': ['PROD_GLASS_A1', 'PROD_GLASS_B2', 'PROD_GLASS_C3'],
    'WAREHOUSES': ['WAREHOUSE_US_01', 'WAREHOUSE_EU_01', 'WAREHOUSE_APAC_01', 
                   'WAREHOUSE_US_02', 'WAREHOUSE_APAC_02', 'WAREHOUSE_EU_02'],
    'MACHINES': ['MACHINE_LINE_01', 'MACHINE_LINE_02', 'MACHINE_LINE_03',
                 'MACHINE_LINE_04', 'MACHINE_LINE_05', 'MACHINE_LINE_06', 'MACHINE_LINE_07'],
    'SUPPLIERS': ['SUP_GLASS_RAW_01', 'SUP_GLASS_RAW_02', 'SUP_METAL_FRAME_01',
                  'SUP_METAL_FRAME_02', 'SUP_ADHESIVE_01', 'SUP_ADHESIVE_02',
                  'SUP_LOGISTICS_01', 'SUP_LOGISTICS_02', 'SUP_LOGISTICS_03',
                  'SUP_PACKAGING_01', 'SUP_PACKAGING_02'],
    'DEFECT_TYPES': ['CRACK', 'BUBBLE', 'DISCOLORATION', 'DIMENSION_OFF', 'SURFACE_SCRATCH', 'OTHER'],
    'STATUSES': ['PENDING', 'IN_TRANSIT', 'DELIVERED', 'DELAYED', 'CANCELLED'],
}

# Anomaly scenarios to simulate occasionally
ANOMALY_SCENARIOS = {
    'machine_failure': 0.15,  # 15% chance
    'quality_issue': 0.2,      # 20% chance
    'supply_delay': 0.1,       # 10% chance
    'shipment_delay': 0.15,    # 15% chance
}

# ============================================================================
# PRODUCTION DATA GENERATION
# ============================================================================

def generate_production_data(date, num_records=12):
    """
    Generate production records for the given date.
    
    Parameters:
        date (str): Date in format YYYY-MM-DD
        num_records (int): Number of production records to generate
    
    Returns:
        pd.DataFrame: Production data
    """
    data = []
    
    for i in range(num_records):
        plant = np.random.choice(CONFIG['PLANTS'])
        product = np.random.choice(CONFIG['PRODUCTS'])
        machine = np.random.choice(CONFIG['MACHINES'])
        
        # Base production quantity
        quantity = np.random.randint(3000, 7000)
        
        # Simulate machine failure anomaly
        downtime = 0
        if np.random.random() < ANOMALY_SCENARIOS['machine_failure']:
            downtime = np.random.randint(30, 120)  # 30-120 minutes downtime
            quantity = int(quantity * 0.7)  # Reduce output by 30%
            logger.warning(f"Machine failure on {machine}: {downtime} min downtime")
        else:
            downtime = np.random.randint(0, 30)
        
        # Operating parameters
        temperature = np.random.normal(850, 15)  # Mean 850°C, std 15
        temperature = np.clip(temperature, 800, 900)  # Ensure realistic range
        
        energy = quantity * 0.9 + np.random.normal(0, 200)  # ~0.9 kWh per unit
        energy = max(energy, 0)
        
        data.append({
            'production_id': f"prod_{date.replace('-', '')}_{'%03d' % (i+1)}",
            'date': date,
            'plant_id': plant,
            'product_id': product,
            'quantity_produced': int(quantity),
            'machine_id': machine,
            'temperature': round(temperature, 1),
            'energy_consumption': round(energy, 2),
            'downtime_minutes': int(downtime)
        })
    
    return pd.DataFrame(data)

# ============================================================================
# SHIPMENT DATA GENERATION
# ============================================================================

def generate_shipment_data(date, num_records=10, carry_over_shipments=None):
    """
    Generate shipment records, accounting for ongoing shipments from previous days.
    
    Parameters:
        date (str): Date in format YYYY-MM-DD
        num_records (int): Number of new shipment records
        carry_over_shipments (list): Shipments from previous days to update
    
    Returns:
        pd.DataFrame: Shipment data
    """
    data = []
    
    # Define route information (origin → destination)
    routes = [
        ('WAREHOUSE_US_01', 'WAREHOUSE_EU_02'),
        ('WAREHOUSE_US_01', 'WAREHOUSE_APAC_01'),
        ('WAREHOUSE_EU_01', 'WAREHOUSE_US_02'),
        ('WAREHOUSE_APAC_01', 'WAREHOUSE_US_01'),
        ('WAREHOUSE_US_01', 'WAREHOUSE_AU_01'),  # Australia
        ('WAREHOUSE_EU_01', 'WAREHOUSE_APAC_02'),
    ]
    
    # Generate new shipments
    for i in range(num_records):
        product = np.random.choice(CONFIG['PRODUCTS'])
        origin, destination = random.choice(routes)
        supplier = np.random.choice(CONFIG['SUPPLIERS'])
        
        # Calculate expected delivery days based on route
        if 'WAREHOUSE_AU' in destination:
            expected_days = np.random.randint(20, 25)
        elif 'WAREHOUSE_EU' in destination and 'WAREHOUSE_US' in origin:
            expected_days = np.random.randint(8, 12)
        elif 'WAREHOUSE_APAC' in destination and 'WAREHOUSE_US' in origin:
            expected_days = np.random.randint(12, 18)
        else:
            expected_days = np.random.randint(5, 10)
        
        dispatch_date = date
        expected_delivery = (datetime.strptime(date, '%Y-%m-%d') + 
                           timedelta(days=expected_days)).strftime('%Y-%m-%d')
        
        # Determine status and delays
        status = 'PENDING'
        actual_delivery = None
        delay_days = 0
        
        # 20% chance dispatch happened in past (IN_TRANSIT or DELIVERED)
        if np.random.random() < 0.6:
            dispatch_date = (datetime.strptime(date, '%Y-%m-%d') - 
                           timedelta(days=np.random.randint(1, 10))).strftime('%Y-%m-%d')
            
            # Check if should be delivered
            if np.random.random() < 0.7:
                status = 'DELIVERED'
                # With 15% probability, it's delayed
                if np.random.random() < ANOMALY_SCENARIOS['shipment_delay']:
                    delay_days = np.random.randint(1, 5)
                    logger.warning(f"Shipment delay detected: {delay_days} days late")
                
                actual_delivery = (datetime.strptime(expected_delivery, '%Y-%m-%d') + 
                                 timedelta(days=delay_days)).strftime('%Y-%m-%d')
            else:
                status = 'IN_TRANSIT'
        
        data.append({
            'shipment_id': f"ship_{date.replace('-', '')}_{'%03d' % (i+1)}",
            'order_id': f"PO_2026_{date[5:7]}_{str(i+1).zfill(3)}",
            'product_id': product,
            'quantity': np.random.randint(500, 2500),
            'origin': origin,
            'destination': destination,
            'supplier_id': supplier,
            'dispatch_date': dispatch_date,
            'expected_delivery_date': expected_delivery,
            'actual_delivery_date': actual_delivery,
            'delay_days': delay_days,
            'status': status
        })
    
    return pd.DataFrame(data)

# ============================================================================
# INVENTORY DATA GENERATION
# ============================================================================

def generate_inventory_data(date, production_df, shipment_df):
    """
    Generate inventory records using production and shipment data.
    Maintains conservation of stock across days.
    
    Parameters:
        date (str): Date in format YYYY-MM-DD
        production_df (pd.DataFrame): Production data for the day
        shipment_df (pd.DataFrame): Shipment data for the day
    
    Returns:
        pd.DataFrame: Inventory data
    """
    data = []
    inventory_idx = 0
    
    # Aggregate production by product and warehouse
    for product in CONFIG['PRODUCTS']:
        for warehouse in CONFIG['WAREHOUSES']:
            inventory_idx += 1
            
            # Opening stock (simulated based on product and warehouse)
            opening_stock = np.random.randint(4000, 15000)
            
            # Today's production (only from matching warehouse's plant)
            produced = production_df[
                production_df['product_id'] == product
            ]['quantity_produced'].sum()
            
            # Today's shipments (only from matching warehouse)
            shipped = shipment_df[
                (shipment_df['product_id'] == product) &
                (shipment_df['origin'] == warehouse) &
                (shipment_df['status'].isin(['DELIVERED', 'IN_TRANSIT']))
            ]['quantity'].sum()
            
            # Ensure we don't ship more than available
            available = opening_stock + produced
            if shipped > available:
                shipped = max(0, available - 1000)  # Keep min buffer
            
            closing_stock = opening_stock + produced - shipped
            
            data.append({
                'inventory_id': f"inv_{date.replace('-', '')}_{'%02d' % inventory_idx}",
                'date': date,
                'product_id': product,
                'warehouse_id': warehouse,
                'opening_stock': int(opening_stock),
                'produced': int(produced),
                'shipped': int(shipped),
                'closing_stock': int(closing_stock)
            })
    
    return pd.DataFrame(data)

# ============================================================================
# SUPPLIER DATA GENERATION
# ============================================================================

def generate_supplier_data(date, num_deliveries=11):
    """
    Generate supplier delivery records.
    
    Parameters:
        date (str): Date in format YYYY-MM-DD
        num_deliveries (int): Number of supplier records
    
    Returns:
        pd.DataFrame: Supplier data
    """
    data = []
    
    for i, supplier in enumerate(CONFIG['SUPPLIERS'][:num_deliveries]):
        expected_date = (datetime.strptime(date, '%Y-%m-%d') - 
                        timedelta(days=np.random.randint(0, 5))).strftime('%Y-%m-%d')
        
        # Simulate supply delays with 10% probability
        delay = 0
        if np.random.random() < ANOMALY_SCENARIOS['supply_delay']:
            delay = np.random.randint(1, 3)
            logger.warning(f"Supplier {supplier} delay: {delay} days")
        
        delivery_date = (datetime.strptime(expected_date, '%Y-%m-%d') + 
                        timedelta(days=delay)).strftime('%Y-%m-%d')
        
        # Quality rating (0-100)
        quality = np.random.normal(91, 3)
        quality = np.clip(quality, 75, 100)
        
        data.append({
            'supplier_id': supplier,
            'supplier_name': f"Supplier_{supplier.split('_')[-1]}",
            'material_type': np.random.choice(['Raw Materials', 'Components', 'Packaging', 'Logistics']),
            'delivery_date': delivery_date,
            'expected_date': expected_date,
            'delay_days': delay,
            'quality_rating': round(quality, 1)
        })
    
    return pd.DataFrame(data)

# ============================================================================
# QUALITY DATA GENERATION
# ============================================================================

def generate_quality_data(date, num_batches=12):
    """
    Generate quality control records.
    
    Parameters:
        date (str): Date in format YYYY-MM-DD
        num_batches (int): Number of quality records
    
    Returns:
        pd.DataFrame: Quality data
    """
    data = []
    
    for i in range(num_batches):
        product = np.random.choice(CONFIG['PRODUCTS'])
        defect_type = np.random.choice(CONFIG['DEFECT_TYPES'])
        
        # Base defect rate
        base_defect_rate = np.random.uniform(0.1, 1.5)
        
        # Simulate quality issue anomaly (20% probability)
        if np.random.random() < ANOMALY_SCENARIOS['quality_issue']:
            base_defect_rate = np.random.uniform(2, 5)
            logger.warning(f"Quality issue detected in batch {i+1}: {base_defect_rate:.2f}% defect rate")
        
        # Calculate defect count
        batch_size = np.random.randint(4000, 10000)
        defects_count = max(0, int(batch_size * base_defect_rate / 100))
        
        data.append({
            'quality_id': f"qual_{date.replace('-', '')}_{'%03d' % (i+1)}",
            'date': date,
            'product_id': product,
            'batch_id': f"BATCH_{date.replace('-', '_')}_{'%03d' % (i+1)}",
            'defects_count': defects_count,
            'defect_type': defect_type,
            'defect_rate': round(base_defect_rate, 2)
        })
    
    return pd.DataFrame(data)

# ============================================================================
# FILE OPERATIONS
# ============================================================================

def ensure_directories():
    """Create necessary directories if they don't exist."""
    for directory in [CONFIG['RAW_DATA_PATH'], CONFIG['PROCESSED_DATA_PATH']]:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory: {directory}")

def append_or_create_csv(df, filepath, table_name):
    """
    Append DataFrame to CSV file if it exists, otherwise create it.
    Removes duplicates based on ID column and keeps most recent data.
    
    Parameters:
        df (pd.DataFrame): Data to append
        filepath (str): Path to CSV file
        table_name (str): Name of table for logging
    """
    if os.path.exists(filepath):
        existing_df = pd.read_csv(filepath)
        
        # Combine and remove duplicates (keep latest)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        
        # Get ID column name dynamically
        id_col = [col for col in combined_df.columns if 'id' in col.lower()][0]
        combined_df = combined_df.drop_duplicates(subset=[id_col], keep='last')
        
        combined_df.to_csv(filepath, index=False)
        logger.info(f"Appended {len(df)} records to {table_name} → {filepath}")
    else:
        df.to_csv(filepath, index=False)
        logger.info(f"Created new {table_name} file → {filepath}")

def save_daily_files(date):
    """
    Save all daily data files for the given date.
    
    Parameters:
        date (str): Date in format YYYY-MM-DD
    """
    ensure_directories()
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Generating data for {date}")
    logger.info(f"{'='*70}\n")
    
    # Generate production data
    production_df = generate_production_data(date)
    
    # Generate shipment data
    shipment_df = generate_shipment_data(date)
    
    # Generate inventory data
    inventory_df = generate_inventory_data(date, production_df, shipment_df)
    
    # Generate supplier data
    supplier_df = generate_supplier_data(date)
    
    # Generate quality data
    quality_df = generate_quality_data(date)
    
    # Save to daily files (OPTION B - separate per day)
    today_date_formatted = date.replace('-', '_')
    
    append_or_create_csv(production_df, 
                        f"{CONFIG['RAW_DATA_PATH']}/production_{today_date_formatted}.csv",
                        "Production")
    
    append_or_create_csv(shipment_df,
                        f"{CONFIG['RAW_DATA_PATH']}/shipments_{today_date_formatted}.csv",
                        "Shipments")
    
    append_or_create_csv(inventory_df,
                        f"{CONFIG['RAW_DATA_PATH']}/inventory_{today_date_formatted}.csv",
                        "Inventory")
    
    append_or_create_csv(supplier_df,
                        f"{CONFIG['RAW_DATA_PATH']}/suppliers_{today_date_formatted}.csv",
                        "Suppliers")
    
    append_or_create_csv(quality_df,
                        f"{CONFIG['RAW_DATA_PATH']}/quality_{today_date_formatted}.csv",
                        "Quality")
    
    logger.info(f"\n✓ Data generation completed for {date}\n")
    
    return {
        'production': len(production_df),
        'shipments': len(shipment_df),
        'inventory': len(inventory_df),
        'suppliers': len(supplier_df),
        'quality': len(quality_df)
    }

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate daily supply chain data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_daily_data.py                 # Generate for today
  python scripts/generate_daily_data.py --date 2026-04-05  # Generate specific date
  python scripts/generate_daily_data.py --backfill 7    # Generate last 7 days
        """
    )
    
    parser.add_argument('--date', type=str, default=None,
                       help='Date in format YYYY-MM-DD (default: today)')
    parser.add_argument('--backfill', type=int, default=None,
                       help='Number of days to backfill (generates last N days)')
    
    args = parser.parse_args()
    
    # Determine dates to generate
    if args.backfill:
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') 
                for i in range(args.backfill-1, -1, -1)]
    elif args.date:
        dates = [args.date]
    else:
        dates = [datetime.now().strftime('%Y-%m-%d')]
    
    # Generate data for all specified dates
    summary = {}
    for date in dates:
        summary[date] = save_daily_files(date)
    
    # Print summary
    logger.info(f"{'='*70}")
    logger.info("DATA GENERATION SUMMARY")
    logger.info(f"{'='*70}")
    for date, counts in summary.items():
        logger.info(f"\n{date}:")
        for table, count in counts.items():
            logger.info(f"  {table:12s}: {count:3d} records")

if __name__ == '__main__':
    main()
