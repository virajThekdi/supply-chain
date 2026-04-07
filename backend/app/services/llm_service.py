"""
LLM / RAG Integration Service

Integrates with local LLM (Ollama) for intelligent Q&A.
Uses ChromaDB for vector embeddings and RAG (Retrieval-Augmented Generation).

Features:
- Load CSV data into vector store
- Retrieve relevant context for queries
- Generate LLM responses with source attribution
- Maintain conversation context
"""

import json
import logging
from typing import Optional, List, Tuple
from datetime import datetime
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

class LLMService:
    """
    LLM service for intelligent queries about supply chain data.
    
    In production, this would use:
    - ChromaDB for vector embeddings
    - Ollama for local LLM (e.g., Llama 2, Mistral)
    
    For this demo, we'll provide a rule-based system that simulates RAG.
    """
    
    def __init__(self, data_path: str = 'data/raw'):
        """
        Initialize LLM service.
        
        Args:
            data_path: Path to CSV data files
        """
        self.data_path = Path(data_path)
        self.conversation_history = {}
        self.data_cache = {}
        self.load_data()
        
        logger.info("LLM Service initialized (Rule-based simulation)")
    
    def load_data(self):
        """Load CSV data for RAG retrieval."""
        try:
            import pandas as pd
            
            # Load latest files
            for file_pattern, key in [
                ('shipments_*.csv', 'shipments'),
                ('quality_*.csv', 'quality'),
                ('production_*.csv', 'production'),
                ('inventory_*.csv', 'inventory'),
                ('suppliers_*.csv', 'suppliers')
            ]:
                files = sorted(self.data_path.glob(file_pattern))
                if files:
                    self.data_cache[key] = pd.read_csv(files[-1])
                    logger.info(f"Loaded {key} data: {len(self.data_cache[key])} rows")
        
        except Exception as e:
            logger.error(f"Error loading data for RAG: {e}")
    
    # ========================================================================
    # QUERY ROUTING
    # ========================================================================
    
    def process_query(self, query: str, context: Optional[str] = None) -> Tuple[str, List[str]]:
        """
        Process user query and generate AI response with RAG.
        
        Args:
            query: User question
            context: Optional context (product ID, date range, etc.)
        
        Returns:
            Tuple of (response_text, sources_used)
        """
        # Determine query type
        query_lower = query.lower()
        sources = []
        
        if any(word in query_lower for word in ['delay', 'late', 'delivery']):
            response, sources = self._answer_delivery_query(query, context)
        elif any(word in query_lower for word in ['defect', 'quality', 'fault', 'problem']):
            response, sources = self._answer_quality_query(query, context)
        elif any(word in query_lower for word in ['inventory', 'stock', 'warehouse']):
            response, sources = self._answer_inventory_query(query, context)
        elif any(word in query_lower for word in ['production', 'output', 'produce']):
            response, sources = self._answer_production_query(query, context)
        elif any(word in query_lower for word in ['supplier', 'vendor']):
            response, sources = self._answer_supplier_query(query, context)
        else:
            response, sources = self._answer_general_query(query, context)
        
        return response, sources
    
    # ========================================================================
    # QUERY HANDLERS
    # ========================================================================
    
    def _answer_delivery_query(self, query: str, context: Optional[str]) -> Tuple[str, List[str]]:
        """Handle delivery/delay related queries."""
        sources = ['shipments']
        
        if 'shipments' not in self.data_cache:
            return "No shipment data available.", sources
        
        df = self.data_cache['shipments']
        
        # Calculate delivery KPIs
        delivered = df[df['status'] == 'DELIVERED']
        on_time = len(delivered[delivered['delay_days'] == 0])
        total_delivered = len(delivered)
        on_time_rate = (on_time / total_delivered * 100) if total_delivered > 0 else 0
        
        avg_delay = df[df['delay_days'] > 0]['delay_days'].mean()
        
        # Check for specific product
        if context:
            product_df = df[df['product_id'].str.contains(context, case=False, na=False)]
            if len(product_df) > 0:
                product_on_time = len(
                    product_df[(product_df['status'] == 'DELIVERED') & 
                              (product_df['delay_days'] == 0)]
                )
                response = (
                    f"For {context}: {product_on_time} out of {len(product_df)} shipped orders "
                    f"were delivered on-time. Average delay for this product is "
                    f"{product_df['delay_days'].mean():.1f} days."
                )
            else:
                response = (
                    f"Overall on-time delivery rate: {on_time_rate:.1f}% ({on_time}/{total_delivered}). "
                    f"Average delay for delayed shipments: {avg_delay:.1f} days. "
                    f"No specific data for {context}."
                )
        else:
            response = (
                f"📊 **Delivery Performance:**\\n"
                f"- On-time rate: {on_time_rate:.1f}% ({on_time}/{total_delivered} shipments)\\n"
                f"- Average delay: {avg_delay:.1f} days\\n"
                f"- Total shipments: {len(df)}"
            )
        
        return response, sources
    
    def _answer_quality_query(self, query: str, context: Optional[str]) -> Tuple[str, List[str]]:
        """Handle quality/defect related queries."""
        sources = ['quality']
        
        if 'quality' not in self.data_cache:
            return "No quality data available.", sources
        
        df = self.data_cache['quality']
        
        avg_defect_rate = df['defect_rate'].mean()
        max_defect_rate = df['defect_rate'].max()
        total_defects = df['defects_count'].sum()
        
        # Most common defect
        defect_counts = df['defect_type'].value_counts()
        most_common_defect = defect_counts.index[0] if len(defect_counts) > 0 else "UNKNOWN"
        
        if context:
            product_df = df[df['product_id'].str.contains(context, case=False, na=False)]
            if len(product_df) > 0:
                response = (
                    f"Product {context}:\\n"
                    f"- Average defect rate: {product_df['defect_rate'].mean():.2f}%\\n"
                    f"- Total defects: {product_df['defects_count'].sum()}\\n"
                    f"- Most common defect type: {product_df['defect_type'].mode().values[0] if len(product_df) > 0 else 'N/A'}"
                )
            else:
                response = f"No quality data found for product {context}."
        else:
            response = (
                f"📊 **Quality Metrics:**\\n"
                f"- Average defect rate: {avg_defect_rate:.2f}%\\n"
                f"- Highest defect rate: {max_defect_rate:.2f}%\\n"
                f"- Total defects: {int(total_defects)}\\n"
                f"- Most common defect: {most_common_defect}"
            )
        
        return response, sources
    
    def _answer_inventory_query(self, query: str, context: Optional[str]) -> Tuple[str, List[str]]:
        """Handle inventory/stock related queries."""
        sources = ['inventory']
        
        if 'inventory' not in self.data_cache:
            return "No inventory data available.", sources
        
        df = self.data_cache['inventory']
        
        total_stock = df['closing_stock'].sum()
        avg_stock = df['closing_stock'].mean()
        low_stock = df[df['closing_stock'] < 5000]['product_id'].unique()
        
        if context:
            warehouse_df = df[df['warehouse_id'].str.contains(context, case=False, na=False)]
            if len(warehouse_df) > 0:
                response = (
                    f"Warehouse {context}:\\n"
                    f"- Total stock: {warehouse_df['closing_stock'].sum()} units\\n"
                    f"- Number of products: {warehouse_df['product_id'].nunique()}\\n"
                    f"- Average product stock: {warehouse_df['closing_stock'].mean():.0f} units"
                )
            else:
                response = f"No inventory data found for {context}."
        else:
            response = (
                f"📊 **Inventory Overview:**\\n"
                f"- Total stock: {total_stock:,} units\\n"
                f"- Average product stock: {avg_stock:.0f} units\\n"
                f"- Products with critical stock (<5000): {len(low_stock)}\\n"
                f"- Critical products: {', '.join(low_stock) if len(low_stock) > 0 else 'None'}"
            )
        
        return response, sources
    
    def _answer_production_query(self, query: str, context: Optional[str]) -> Tuple[str, List[str]]:
        """Handle production related queries."""
        sources = ['production']
        
        if 'production' not in self.data_cache:
            return "No production data available.", sources
        
        df = self.data_cache['production']
        
        total_produced = df['quantity_produced'].sum()
        avg_downtime = df['downtime_minutes'].mean()
        
        if context:
            product_df = df[df['product_id'].str.contains(context, case=False, na=False)]
            if len(product_df) > 0:
                response = (
                    f"Production of {context}:\\n"
                    f"- Total produced: {product_df['quantity_produced'].sum():,} units\\n"
                    f"- Average downtime: {product_df['downtime_minutes'].mean():.1f} min\\n"
                    f"- Production runs: {len(product_df)}"
                )
            else:
                response = f"No production data found for {context}."
        else:
            response = (
                f"📊 **Production Summary:**\\n"
                f"- Total units produced: {total_produced:,}\\n"
                f"- Average machine downtime: {avg_downtime:.1f} minutes\\n"
                f"- Active lines: {df['machine_id'].nunique()}"
            )
        
        return response, sources
    
    def _answer_supplier_query(self, query: str, context: Optional[str]) -> Tuple[str, List[str]]:
        """Handle supplier related queries."""
        sources = ['suppliers']
        
        if 'suppliers' not in self.data_cache:
            return "No supplier data available.", sources
        
        df = self.data_cache['suppliers']
        
        avg_rating = df['quality_rating'].mean()
        on_time_count = len(df[df['delay_days'] == 0])
        on_time_rate = (on_time_count / len(df) * 100) if len(df) > 0 else 0
        avg_delay = df['delay_days'].mean()
        
        if context:
            supplier_df = df[df['supplier_id'].str.contains(context, case=False, na=False)]
            if len(supplier_df) > 0:
                response = (
                    f"Supplier {context}:\\n"
                    f"- Quality rating: {supplier_df['quality_rating'].mean():.1f}/100\\n"
                    f"- On-time delivery rate: {(len(supplier_df[supplier_df['delay_days'] == 0]) / len(supplier_df) * 100):.1f}%\\n"
                    f"- Average delay: {supplier_df['delay_days'].mean():.1f} days"
                )
            else:
                response = f"No data found for supplier {context}."
        else:
            response = (
                f"📊 **Supplier Performance:**\\n"
                f"- Average quality rating: {avg_rating:.1f}/100\\n"
                f"- On-time delivery: {on_time_rate:.1f}% ({on_time_count}/{len(df)})\\n"
                f"- Average delay: {avg_delay:.1f} days"
            )
        
        return response, sources
    
    def _answer_general_query(self, query: str, context: Optional[str]) -> Tuple[str, List[str]]:
        """Handle general/unknown queries."""
        sources = ['general_knowledge']
        
        response = (
            f"I understand you're asking: '{query}'\\n\\n"
            f"I can help with questions about:\\n"
            f"- **Delivery & Shipments**: On-time performance, delays, delivery routes\\n"
            f"- **Quality & Defects**: Defect rates, product quality, batch issues\\n"
            f"- **Inventory & Stock**: Warehouse levels, stock status, SKU availability\\n"
            f"- **Production**: Output volume, machine downtime, efficiency\\n"
            f"- **Suppliers**: Performance ratings, delivery reliability, quality scores\\n\\n"
            f"Try asking something like 'What's our on-time delivery rate?' or "
            f"'Show me defect trends for PROD_GLASS_A1'"
        )
        
        return response, sources
    
    # ========================================================================
    # CONVERSATION MANAGEMENT
    # ========================================================================
    
    def init_conversation(self) -> str:
        """Initialize a new conversation."""
        conversation_id = str(uuid.uuid4())
        self.conversation_history[conversation_id] = []
        logger.info(f"Initialized conversation: {conversation_id}")
        return conversation_id
    
    def add_to_conversation(self, conversation_id: str, role: str, message: str):
        """Add message to conversation history."""
        if conversation_id not in self.conversation_history:
            self.conversation_history[conversation_id] = []
        
        self.conversation_history[conversation_id].append({
            'role': role,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_conversation_context(self, conversation_id: str, max_messages: int = 5) -> str:
        """Get recent conversation context for better responses."""
        if conversation_id not in self.conversation_history:
            return ""
        
        history = self.conversation_history[conversation_id][-max_messages:]
        context = "\\n".join([
            f"{msg['role'].upper()}: {msg['message']}" for msg in history
        ])
        return context
    
    # ========================================================================
    # CONFIDENCE SCORING
    # ========================================================================
    
    @staticmethod
    def calculate_confidence(sources: List[str], query_quality: float = 0.9) -> float:
        """
        Calculate confidence score for response.
        
        Args:
            sources: List of data sources used
            query_quality: How well the query matched available data
        
        Returns:
            Confidence score (0-1)
        """
        # Base confidence from source count
        source_confidence = min(len(sources) / 3, 1.0)  # Max 3 relevant sources
        
        # Combine with query quality
        confidence = (source_confidence + query_quality) / 2
        
        return round(confidence, 2)
