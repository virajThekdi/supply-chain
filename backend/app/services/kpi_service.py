"""
KPI Calculation Service

Calculates all key performance indicators for the supply chain including:
- Delivery performance (on-time rate, average delay)
- Quality metrics (defect rates)
- Production efficiency
- Supplier performance
- Inventory turnover
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

class KPICalculator:
    """Calculate KPIs from raw supply chain data."""
    
    def __init__(self, data_path: str = 'data/raw'):
        """
        Initialize KPI calculator.
        
        Args:
            data_path: Path to raw data files
        """
        self.data_path = Path(data_path)
        self.shipments_df = None
        self.production_df = None
        self.quality_df = None
        self.inventory_df = None
        self.supplier_df = None
        self.load_data()
    
    def load_data(self):
        """Load all available data files."""
        try:
            # Load latest files (most recent date)
            # In production, you'd aggregate all files
            csv_files = sorted(self.data_path.glob('shipments_*.csv'))
            if csv_files:
                self.shipments_df = pd.read_csv(csv_files[-1])
                self.shipments_df['dispatch_date'] = pd.to_datetime(
                    self.shipments_df['dispatch_date']
                )
                self.shipments_df['expected_delivery_date'] = pd.to_datetime(
                    self.shipments_df['expected_delivery_date']
                )
                self.shipments_df['actual_delivery_date'] = pd.to_datetime(
                    self.shipments_df['actual_delivery_date'], errors='coerce'
                )
            
            csv_files = sorted(self.data_path.glob('production_*.csv'))
            if csv_files:
                self.production_df = pd.read_csv(csv_files[-1])
                self.production_df['date'] = pd.to_datetime(self.production_df['date'])
            
            csv_files = sorted(self.data_path.glob('quality_*.csv'))
            if csv_files:
                self.quality_df = pd.read_csv(csv_files[-1])
                self.quality_df['date'] = pd.to_datetime(self.quality_df['date'])
            
            csv_files = sorted(self.data_path.glob('inventory_*.csv'))
            if csv_files:
                self.inventory_df = pd.read_csv(csv_files[-1])
                self.inventory_df['date'] = pd.to_datetime(self.inventory_df['date'])
            
            csv_files = sorted(self.data_path.glob('suppliers_*.csv'))
            if csv_files:
                self.supplier_df = pd.read_csv(csv_files[-1])
                self.supplier_df['delivery_date'] = pd.to_datetime(
                    self.supplier_df['delivery_date']
                )
                self.supplier_df['expected_date'] = pd.to_datetime(
                    self.supplier_df['expected_date']
                )
            
            logger.info("Data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    # ========================================================================
    # DELIVERY METRICS
    # ========================================================================
    
    def calculate_on_time_delivery_rate(self) -> Tuple[float, int, int]:
        """
        Calculate percentage of shipments delivered on-time.
        
        Returns:
            Tuple of (on_time_rate_percentage, on_time_count, total_count)
        """
        if self.shipments_df is None or len(self.shipments_df) == 0:
            return 0.0, 0, 0
        
        # Filter delivered shipments
        delivered = self.shipments_df[
            self.shipments_df['status'] == 'DELIVERED'
        ].copy()
        
        if len(delivered) == 0:
            return 0.0, 0, len(self.shipments_df)
        
        # On-time = delay_days = 0
        on_time = len(delivered[delivered['delay_days'] == 0])
        total = len(delivered)
        
        rate = (on_time / total * 100) if total > 0 else 0
        
        logger.info(f"On-time delivery rate: {rate:.2f}% ({on_time}/{total})")
        
        return rate, on_time, total
    
    def calculate_average_delay(self) -> Tuple[float, int]:
        """
        Calculate average delay for delayed shipments.
        
        Returns:
            Tuple of (avg_delay_days, delayed_count)
        """
        if self.shipments_df is None or len(self.shipments_df) == 0:
            return 0.0, 0
        
        delayed = self.shipments_df[
            (self.shipments_df['status'] == 'DELAYED') |
            (self.shipments_df['delay_days'] > 0)
        ]
        
        if len(delayed) == 0:
            return 0.0, 0
        
        avg_delay = delayed['delay_days'].mean()
        
        logger.info(f"Average delay: {avg_delay:.2f} days ({len(delayed)} shipments)")
        
        return avg_delay, len(delayed)
    
    # ========================================================================
    # QUALITY METRICS
    # ========================================================================
    
    def calculate_defect_metrics(self) -> Dict:
        """
        Calculate quality metrics including defect rates and trends.
        
        Returns:
            Dictionary with defect statistics
        """
        if self.quality_df is None or len(self.quality_df) == 0:
            return {
                'avg_defect_rate': 0.0,
                'max_defect_rate': 0.0,
                'min_defect_rate': 0.0,
                'total_defects': 0,
                'by_product': {},
                'by_defect_type': {}
            }
        
        # Overall metrics
        avg_defect = self.quality_df['defect_rate'].mean()
        max_defect = self.quality_df['defect_rate'].max()
        total_defects = self.quality_df['defects_count'].sum()
        
        # By product
        by_product = {}
        for product in self.quality_df['product_id'].unique():
            product_data = self.quality_df[
                self.quality_df['product_id'] == product
            ]
            by_product[product] = {
                'avg_defect_rate': product_data['defect_rate'].mean(),
                'defects_count': product_data['defects_count'].sum()
            }
        
        # By defect type
        by_type = {}
        for defect_type in self.quality_df['defect_type'].unique():
            type_data = self.quality_df[
                self.quality_df['defect_type'] == defect_type
            ]
            by_type[defect_type] = {
                'count': len(type_data),
                'total_defects': type_data['defects_count'].sum()
            }
        
        # Get highest defect product
        highest_product = max(
            by_product.items(),
            key=lambda x: x[1]['avg_defect_rate']
        )[0] if by_product else None
        
        result = {
            'avg_defect_rate': round(avg_defect, 2),
            'max_defect_rate': round(max_defect, 2),
            'total_defects': int(total_defects),
            'highest_defect_product': highest_product,
            'by_product': by_product,
            'by_defect_type': by_type
        }
        
        logger.info(f"Quality metrics: {result['avg_defect_rate']:.2f}% avg defect rate")
        
        return result
    
    # ========================================================================
    # PRODUCTION METRICS
    # ========================================================================
    
    def calculate_production_metrics(self) -> Dict:
        """Calculate production volume and efficiency metrics."""
        if self.production_df is None or len(self.production_df) == 0:
            return {
                'total_volume': 0,
                'avg_downtime': 0,
                'efficiency': 0,
                'avg_temperature': 0,
                'avg_energy_per_unit': 0
            }
        
        total_volume = self.production_df['quantity_produced'].sum()
        avg_downtime = self.production_df['downtime_minutes'].mean()
        avg_energy = self.production_df['energy_consumption'].sum() / max(total_volume, 1)
        avg_temp = self.production_df['temperature'].mean()
        
        # Efficiency: (actual output / potential output) * 100
        # Potential = if no downtime
        max_possible = (
            self.production_df['quantity_produced'].sum() +
            self.production_df['downtime_minutes'].sum() / 60 * 100  # rough estimate
        )
        efficiency = (total_volume / max_possible * 100) if max_possible > 0 else 100
        
        result = {
            'total_volume': int(total_volume),
            'avg_downtime': round(avg_downtime, 2),
            'efficiency': round(efficiency, 2),
            'avg_temperature': round(avg_temp, 2),
            'avg_energy_per_unit': round(avg_energy, 2),
            'by_plant': self._production_by_plant(),
            'by_machine': self._production_by_machine()
        }
        
        logger.info(f"Production: {total_volume} units, {efficiency:.1f}% efficiency")
        
        return result
    
    def _production_by_plant(self) -> Dict:
        """Get production breakdown by plant."""
        if self.production_df is None:
            return {}
        
        return self.production_df.groupby('plant_id').agg({
            'quantity_produced': 'sum',
            'downtime_minutes': 'mean',
            'temperature': 'mean'
        }).round(2).to_dict('index')
    
    def _production_by_machine(self) -> Dict:
        """Get production breakdown by machine."""
        if self.production_df is None:
            return {}
        
        return self.production_df.groupby('machine_id').agg({
            'quantity_produced': 'sum',
            'downtime_minutes': 'sum'
        }).to_dict('index')
    
    # ========================================================================
    # SUPPLIER METRICS
    # ========================================================================
    
    def calculate_supplier_metrics(self) -> Dict:
        """Calculate supplier performance metrics."""
        if self.supplier_df is None or len(self.supplier_df) == 0:
            return {
                'avg_rating': 0,
                'on_time_rate': 0,
                'avg_delay': 0,
                'by_supplier': {}
            }
        
        avg_rating = self.supplier_df['quality_rating'].mean()
        
        # On-time rate for suppliers
        on_time = len(self.supplier_df[self.supplier_df['delay_days'] == 0])
        on_time_rate = (on_time / len(self.supplier_df) * 100) if len(self.supplier_df) > 0 else 0
        
        avg_delay = self.supplier_df['delay_days'].mean()
        
        # By supplier
        by_supplier = {}
        for supplier_id in self.supplier_df['supplier_id'].unique():
            supplier_data = self.supplier_df[
                self.supplier_df['supplier_id'] == supplier_id
            ]
            by_supplier[supplier_id] = {
                'name': supplier_data['supplier_name'].iloc[0],
                'avg_rating': round(supplier_data['quality_rating'].mean(), 2),
                'on_time_rate': round(
                    (len(supplier_data[supplier_data['delay_days'] == 0]) / 
                     len(supplier_data) * 100),
                    2
                ),
                'avg_delay_days': round(supplier_data['delay_days'].mean(), 2)
            }
        
        # Underperforming suppliers (rating < 85 or on-time < 80%)
        underperforming = [
            supplier_id for supplier_id, metrics in by_supplier.items()
            if metrics['avg_rating'] < 85 or metrics['on_time_rate'] < 80
        ]
        
        result = {
            'avg_rating': round(avg_rating, 2),
            'on_time_rate': round(on_time_rate, 2),
            'avg_delay_days': round(avg_delay, 2),
            'underperforming_suppliers': underperforming,
            'by_supplier': by_supplier
        }
        
        logger.info(f"Supplier metrics: {avg_rating:.1f} avg rating, {on_time_rate:.1f}% on-time")
        
        return result
    
    # ========================================================================
    # INVENTORY METRICS
    # ========================================================================
    
    def calculate_inventory_metrics(self) -> Dict:
        """Calculate inventory turnover and stock levels."""
        if self.inventory_df is None or len(self.inventory_df) == 0:
            return {
                'avg_turnover': 0,
                'by_warehouse': {},
                'low_stock_products': []
            }
        
        # Average turnover = shipped / avg_stock
        avg_shipped_daily = self.inventory_df['shipped'].mean()
        avg_stock = self.inventory_df['closing_stock'].mean()
        
        # Annualized turnover (assuming daily data)
        turnover = (avg_shipped_daily * 365 / avg_stock) if avg_stock > 0 else 0
        
        # By warehouse
        by_warehouse = {}
        for warehouse_id in self.inventory_df['warehouse_id'].unique():
            warehouse_data = self.inventory_df[
                self.inventory_df['warehouse_id'] == warehouse_id
            ]
            total_stock = warehouse_data['closing_stock'].sum()
            by_warehouse[warehouse_id] = {
                'total_stock': int(total_stock),
                'avg_stock': round(warehouse_data['closing_stock'].mean(), 0),
                'utilization_pct': round(
                    (total_stock / 100000 * 100),  # assuming capacity
                    2
                )
            }
        
        # Low stock products (closing_stock < 5000)
        low_stock = self.inventory_df[
            self.inventory_df['closing_stock'] < 5000
        ]['product_id'].unique().tolist()
        
        result = {
            'avg_turnover': round(turnover, 2),
            'by_warehouse': by_warehouse,
            'low_stock_products': low_stock
        }
        
        logger.info(f"Inventory turnover: {turnover:.2f}x annually")
        
        return result
    
    # ========================================================================
    # AGGREGATE ALL KPIs
    # ========================================================================
    
    def calculate_all_kpis(self) -> Dict:
        """Calculate all KPIs in one call."""
        on_time_rate, on_time_count, total_shipped = self.calculate_on_time_delivery_rate()
        avg_delay, delayed_count = self.calculate_average_delay()
        quality_metrics = self.calculate_defect_metrics()
        production_metrics = self.calculate_production_metrics()
        supplier_metrics = self.calculate_supplier_metrics()
        inventory_metrics = self.calculate_inventory_metrics()
        
        kpis = {
            'calculated_at': datetime.now().isoformat(),
            'delivery': {
                'on_time_rate': on_time_rate,
                'on_time_count': on_time_count,
                'total_shipped': total_shipped,
                'avg_delay_days': avg_delay,
                'delayed_count': delayed_count
            },
            'quality': quality_metrics,
            'production': production_metrics,
            'supplier': supplier_metrics,
            'inventory': inventory_metrics
        }
        
        logger.info("All KPIs calculated successfully")
        
        return kpis
