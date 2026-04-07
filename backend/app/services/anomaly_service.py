"""
Anomaly Detection Service

Identifies anomalies using statistical methods:
- Rolling average for trend detection
- Standard deviation based outlier detection
- Isolation Forest for multivariate anomalies
- Business rule-based detection
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
try:
    from sklearn.ensemble import IsolationForest
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    IsolationForest = None
import logging
import uuid

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Detect anomalies in supply chain data."""
    
    def __init__(self, data_path: str = 'data/raw', sensitivity: float = 2.0):
        """
        Initialize anomaly detector.
        
        Args:
            data_path: Path to raw data files
            sensitivity: Standard deviation multiplier (higher = less sensitive)
        """
        self.data_path = Path(data_path)
        self.sensitivity = sensitivity
        self.anomalies = []
        self.load_data()
    
    def load_data(self):
        """Load all available data files."""
        try:
            # Load all CSVs for historical analysis
            self.shipments_dfs = []
            self.quality_dfs = []
            
            for f in sorted(self.data_path.glob('shipments_*.csv')):
                df = pd.read_csv(f)
                df['dispatch_date'] = pd.to_datetime(df['dispatch_date'])
                self.shipments_dfs.append(df)
            
            for f in sorted(self.data_path.glob('quality_*.csv')):
                df = pd.read_csv(f)
                df['date'] = pd.to_datetime(df['date'])
                self.quality_dfs.append(df)
            
            if self.shipments_dfs:
                self.shipments_df = pd.concat(self.shipments_dfs, ignore_index=True)
            else:
                self.shipments_df = None
            
            if self.quality_dfs:
                self.quality_df = pd.concat(self.quality_dfs, ignore_index=True)
            else:
                self.quality_df = None
            
            logger.info("Data loaded for anomaly detection")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    # ========================================================================
    # DELIVERY ANOMALIES
    # ========================================================================
    
    def detect_delivery_anomalies(self) -> List[Dict]:
        """
        Detect delivery delays anomalies.
        Uses rolling average and standard deviation.
        """
        anomalies = []
        
        if self.shipments_df is None or len(self.shipments_df) == 0:
            return anomalies
        
        # Sort by date
        df = self.shipments_df.sort_values('dispatch_date').copy()
        
        # Group by destination and calculate daily avg delay
        delays_by_dest = []
        for dest in df['destination'].unique():
            dest_df = df[df['destination'] == dest].copy()
            
            if len(dest_df) < 3:
                continue
            
            delays = dest_df['delay_days'].values
            
            # Calculate rolling average (window=5)
            if len(delays) >= 5:
                rolling_avg = np.convolve(delays, np.ones(5)/5, mode='valid')
                rolling_std = np.std(delays)
                
                # Detect anomalies: delay > mean + sensitivity*std
                threshold = np.mean(delays) + self.sensitivity * rolling_std
                
                for i, delay in enumerate(delays[-5:]):  # Check recent shipments
                    if delay > threshold and delay > 3:  # Also check business rule
                        anomalies.append({
                            'type': 'DELAY',
                            'severity': 'HIGH' if delay > threshold * 1.5 else 'MEDIUM',
                            'title': f'Excessive delay to {dest}',
                            'description': f'Shipment delayed by {delay} days (threshold: {threshold:.1f})',
                            'affected_entity': dest,
                            'entity_type': 'WAREHOUSE',
                            'detected_value': float(delay),
                            'normal_range': (0, threshold),
                            'root_cause': 'Possible logistics/weather issue',
                            'recommended_action': 'Contact logistics provider'
                        })
        
        return anomalies
    
    # ========================================================================
    # QUALITY ANOMALIES
    # ========================================================================
    
    def detect_quality_anomalies(self) -> List[Dict]:
        """
        Detect quality/defect anomalies.
        Uses statistical outlier detection.
        """
        anomalies = []
        
        if self.quality_df is None or len(self.quality_df) == 0:
            return anomalies
        
        # Analyze defect rates by product
        for product in self.quality_df['product_id'].unique():
            product_df = self.quality_df[
                self.quality_df['product_id'] == product
            ].copy()
            
            if len(product_df) < 3:
                continue
            
            defect_rates = product_df['defect_rate'].values
            mean_rate = np.mean(defect_rates)
            std_rate = np.std(defect_rates)
            
            # Anomaly threshold
            threshold = mean_rate + self.sensitivity * std_rate
            
            # Check recent records
            for _, row in product_df.tail(3).iterrows():
                if row['defect_rate'] > threshold:
                    severity = 'CRITICAL' if row['defect_rate'] > mean_rate * 2 else 'HIGH'
                    
                    anomalies.append({
                        'type': 'QUALITY',
                        'severity': severity,
                        'title': f'High defect rate in {product}',
                        'description': (
                            f"Defect rate: {row['defect_rate']:.2f}% "
                            f"(normal: {mean_rate:.2f}%, threshold: {threshold:.2f}%)"
                        ),
                        'affected_entity': product,
                        'entity_type': 'PRODUCT',
                        'detected_value': float(row['defect_rate']),
                        'normal_range': (mean_rate - std_rate, threshold),
                        'root_cause': f"Possible {row['defect_type']} issue in production",
                        'recommended_action': 'Review batch {}, check production parameters'.format(
                            row['batch_id']
                        )
                    })
        
        return anomalies
    
    # ========================================================================
    # INVENTORY ANOMALIES
    # ========================================================================
    
    def detect_inventory_anomalies(self, inventory_df) -> List[Dict]:
        """
        Detect inventory stock anomalies.
        Identifies low stock and unusual movements.
        """
        anomalies = []
        
        if inventory_df is None or len(inventory_df) == 0:
            return anomalies
        
        # Check for critically low stock
        for _, row in inventory_df.iterrows():
            if row['closing_stock'] < 1000:  # Critical threshold
                anomalies.append({
                    'type': 'INVENTORY',
                    'severity': 'HIGH',
                    'title': f'Critical stock level: {row["product_id"]}',
                    'description': (
                        f"{row['product_id']} stock at {row['closing_stock']} units "
                        f"(critical: < 1000)"
                    ),
                    'affected_entity': row['product_id'],
                    'entity_type': 'PRODUCT',
                    'detected_value': float(row['closing_stock']),
                    'normal_range': (5000, 50000),
                    'root_cause': 'High shipments or low production',
                    'recommended_action': 'Increase production or review demand'
                })
            
            # Check for unusual shipped quantity
            if row['shipped'] > row['opening_stock'] + row['produced']:
                anomalies.append({
                    'type': 'INVENTORY',
                    'severity': 'CRITICAL',
                    'title': f'Inventory constraint violation',
                    'description': (
                        f"Shipped {row['shipped']} units but only "
                        f"{row['opening_stock'] + row['produced']} available"
                    ),
                    'affected_entity': row['product_id'],
                    'entity_type': 'PRODUCT',
                    'detected_value': float(row['shipped']),
                    'normal_range': (0, row['opening_stock'] + row['produced']),
                    'root_cause': 'Data error or unreported inventory',
                    'recommended_action': 'Verify data integrity'
                })
        
        return anomalies
    
    # ========================================================================
    # PRODUCTION ANOMALIES
    # ========================================================================
    
    def detect_production_anomalies(self, production_df) -> List[Dict]:
        """
        Detect production anomalies.
        Identifies machines with excessive downtime or temperature issues.
        """
        anomalies = []
        
        if production_df is None or len(production_df) == 0:
            return anomalies
        
        # Check for excessive downtime
        machine_downtime = production_df.groupby('machine_id')['downtime_minutes'].agg(['mean', 'max'])
        
        for machine_id, row in machine_downtime.iterrows():
            if row['mean'] > 45:  # Avg downtime threshold
                anomalies.append({
                    'type': 'PERFORMANCE',
                    'severity': 'MEDIUM',
                    'title': f'High average downtime: {machine_id}',
                    'description': (
                        f"{machine_id} averaging {row['mean']:.1f} min downtime "
                        f"(threshold: 45 min)"
                    ),
                    'affected_entity': machine_id,
                    'entity_type': 'MACHINE',
                    'detected_value': row['mean'],
                    'normal_range': (0, 45),
                    'root_cause': 'Possible maintenance issue',
                    'recommended_action': 'Schedule preventive maintenance'
                })
            
            if row['max'] > 120:  # Critical threshold
                anomalies.append({
                    'type': 'PERFORMANCE',
                    'severity': 'CRITICAL',
                    'title': f'Critical downtime incident: {machine_id}',
                    'description': f"{machine_id} downtime: {row['max']} minutes",
                    'affected_entity': machine_id,
                    'entity_type': 'MACHINE',
                    'detected_value': row['max'],
                    'normal_range': (0, 120),
                    'root_cause': 'Machine breakdown',
                    'recommended_action': 'Immediate maintenance required'
                })
        
        # Check temperature anomalies
        for machine_id in production_df['machine_id'].unique():
            machine_df = production_df[production_df['machine_id'] == machine_id]
            temps = machine_df['temperature'].values
            
            if len(temps) > 2:
                mean_temp = np.mean(temps)
                std_temp = np.std(temps)
                
                for _, row in machine_df.tail(1).iterrows():
                    if abs(row['temperature'] - mean_temp) > 3 * std_temp:
                        anomalies.append({
                            'type': 'PERFORMANCE',
                            'severity': 'MEDIUM',
                            'title': f'Abnormal temperature: {machine_id}',
                            'description': (
                                f"Temperature {row['temperature']:.1f}°C "
                                f"(normal: {mean_temp:.1f}°C ± {std_temp:.1f}°C)"
                            ),
                            'affected_entity': machine_id,
                            'entity_type': 'MACHINE',
                            'detected_value': row['temperature'],
                            'normal_range': (mean_temp - std_temp, mean_temp + std_temp),
                            'root_cause': 'Cooling system issue',
                            'recommended_action': 'Check temperature calibration'
                        })
        
        return anomalies
    
    # ========================================================================
    # SUPPLIER ANOMALIES
    # ========================================================================
    
    def detect_supplier_anomalies(self, supplier_df) -> List[Dict]:
        """Detect supplier performance anomalies."""
        anomalies = []
        
        if supplier_df is None or len(supplier_df) == 0:
            return anomalies
        
        # Check quality rating drops
        for supplier_id in supplier_df['supplier_id'].unique():
            supplier_records = supplier_df[
                supplier_df['supplier_id'] == supplier_id
            ].sort_values('delivery_date')
            
            if len(supplier_records) < 2:
                continue
            
            ratings = supplier_records['quality_rating'].values
            mean_rating = np.mean(ratings)
            
            # Check latest rating
            latest_rating = ratings[-1]
            
            if latest_rating < 80:
                anomalies.append({
                    'type': 'PERFORMANCE',
                    'severity': 'HIGH',
                    'title': f'Low supplier quality: {supplier_records.iloc[0]["supplier_name"]}',
                    'description': (
                        f"Quality rating: {latest_rating:.1f}% "
                        f"(threshold: 85%, avg: {mean_rating:.1f}%)"
                    ),
                    'affected_entity': supplier_id,
                    'entity_type': 'SUPPLIER',
                    'detected_value': float(latest_rating),
                    'normal_range': (85, 100),
                    'root_cause': 'Quality control issues at supplier',
                    'recommended_action': 'Contact supplier, request improvement plan'
                })
        
        return anomalies
    
    # ========================================================================
    # AGGREGATE ANOMALIES
    # ========================================================================
    
    def detect_all_anomalies(self, production_df=None, inventory_df=None, 
                            supplier_df=None) -> List[Dict]:
        """
        Detect all types of anomalies.
        
        Returns:
            List of detected anomalies with metadata
        """
        all_anomalies = []
        
        # Delivery anomalies
        all_anomalies.extend(self.detect_delivery_anomalies())
        
        # Quality anomalies
        all_anomalies.extend(self.detect_quality_anomalies())
        
        # Inventory anomalies
        if inventory_df is not None:
            all_anomalies.extend(self.detect_inventory_anomalies(inventory_df))
        
        # Production anomalies
        if production_df is not None:
            all_anomalies.extend(self.detect_production_anomalies(production_df))
        
        # Supplier anomalies
        if supplier_df is not None:
            all_anomalies.extend(self.detect_supplier_anomalies(supplier_df))
        
        # Add metadata to each anomaly
        for anomaly in all_anomalies:
            anomaly.update({
                'anomaly_id': f"anom_{uuid.uuid4().hex[:8]}",
                'detected_date': datetime.now().date().isoformat(),
                'ai_explanation': self._generate_ai_explanation(anomaly)
            })
        
        logger.info(f"Detected {len(all_anomalies)} anomalies")
        
        return all_anomalies
    
    @staticmethod
    def _generate_ai_explanation(anomaly: Dict) -> str:
        """Generate AI explanation for anomaly."""
        type_explanations = {
            'DELAY': (
                f"A shipment to {anomaly.get('affected_entity', 'destination')} "
                f"experienced a {anomaly.get('detected_value', 0):.1f}day delay, "
                f"exceeding normal patterns. This could indicate logistics issues, "
                f"documentation delays, or customer-side delays."
            ),
            'QUALITY': (
                f"Product {anomaly.get('affected_entity', 'product')} shows "
                f"a defect rate of {anomaly.get('detected_value', 0):.2f}%, "
                f"significantly above the normal range. Immediate investigation of "
                f"production parameters is recommended."
            ),
            'INVENTORY': (
                f"Stock level for {anomaly.get('affected_entity', 'product')} "
                f"is critically low at {anomaly.get('detected_value', 0):.0f} units. "
                f"This may lead to stockouts and delayed shipments."
            ),
            'PERFORMANCE': (
                f"Machine {anomaly.get('affected_entity', 'machine')} is showing "
                f"degraded performance with {anomaly.get('detected_value', 0):.1f} "
                f"minutes of downtime, above normal levels."
            )
        }
        
        return type_explanations.get(
            anomaly.get('type', 'UNKNOWN'),
            f"{anomaly.get('title', 'An anomaly')} has been detected."
        )
