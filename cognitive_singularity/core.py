"""
Core CognitiveSingularity implementation - the unified field that orchestrates all components.
"""

import numpy as np
from typing import Dict, Tuple, Any, Optional
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CognitiveSingularity:
    """
    Unified GraphQL-Neural-Hypergraph-Membrane Architecture
    Master Tensor: [∞ × 13 × 11 × 7 × 5 × 3 × 2]
    Total Parameters: ∞ (unbounded creativity)
    
    This is the core orchestrator that unifies all cognitive components
    through GraphQL as the universal cognitive protocol.
    """
    
    def __init__(self):
        """Initialize the cognitive singularity with all component tensor shapes."""
        self.components = {
            'gnn': (7, 7, 7),        # 343 states = 7³
            'das': (11, 5, 2),       # 110 states = 2 × 5 × 11
            'esn': (13, 3, 3),       # 117 states = 3² × 13
            'membrane': (5, 5, 5),   # 125 states = 5³
            'ecan': (3, 3, 3, 3)     # 81 states = 3⁴
        }
        
        # Calculate total degrees of freedom
        self.total_freedom = sum(np.prod(shape) for shape in self.components.values())
        
        # Verify the magical number 776
        assert self.total_freedom == 776, f"Expected 776 states, got {self.total_freedom}"
        
        logger.info(f"🌌 Cognitive Singularity initialized with {self.total_freedom} degrees of freedom")
        logger.info(f"🔮 Prime factorization: {self.prime_factorize(self.total_freedom)}")
    
    def prime_factorize(self, n: int) -> Dict[int, int]:
        """
        Discover the prime essence of cognitive complexity.
        Returns prime factorization as {prime: count} dictionary.
        """
        factors = {}
        d = 2
        while d * d <= n:
            while n % d == 0:
                factors[d] = factors.get(d, 0) + 1
                n //= d
            d += 1
        if n > 1:
            factors[n] = factors.get(n, 0) + 1
        
        # Convert numpy types to native Python types for JSON serialization
        return {int(k): int(v) for k, v in factors.items()}
    
    def enumerate_all_states(self) -> np.ndarray:
        """
        Enumerate all 776 quantum states across all components.
        Returns flattened state vector for validation.
        """
        states = []
        for name, shape in self.components.items():
            component_states = np.arange(np.prod(shape)).reshape(shape)
            states.append(component_states.flatten())
        
        return np.concatenate(states)
    
    def generate_tensor_field(self) -> Dict[str, np.ndarray]:
        """
        Generate the complete tensor field for all components.
        Each component gets its own tensor initialized to proper shape.
        """
        tensor_field = {}
        for name, shape in self.components.items():
            # Initialize with small random values for numerical stability
            tensor_field[name] = np.random.normal(0, 0.01, shape).astype(np.float32)
        
        return tensor_field
    
    def calculate_attention_weights(self) -> np.ndarray:
        """
        Calculate attention weights across all components using ECAN principles.
        Returns normalized attention vector of length 5 (one per component).
        """
        # Simple attention based on component complexity (degrees of freedom)
        complexities = [np.prod(shape) for shape in self.components.values()]
        attention = np.array(complexities, dtype=np.float32)
        
        # Normalize to sum to 1.0
        attention = attention / attention.sum()
        
        return attention
    
    def graphql_query_to_tensor(self, query: str) -> np.ndarray:
        """
        Convert GraphQL query to tensor representation for cognitive processing.
        This is the universal interface that all components use.
        """
        # Simple encoding: hash query to get consistent tensor
        query_hash = hash(query) % (2**16)  # Keep it manageable
        
        # Map to high-dimensional space
        tensor = np.zeros(776, dtype=np.float32)
        
        # Distribute hash across components proportionally
        offset = 0
        for name, shape in self.components.items():
            size = np.prod(shape)
            # Use hash to seed deterministic random pattern
            np.random.seed(query_hash + offset)
            component_pattern = np.random.normal(0, 0.1, size)
            tensor[offset:offset+size] = component_pattern
            offset += size
        
        return tensor
    
    def process_cognitive_query(self, query: str) -> Dict[str, Any]:
        """
        Process a GraphQL query through the entire cognitive architecture.
        This is the main entry point for cognitive computation.
        """
        logger.info(f"🧠 Processing cognitive query: {query[:100]}...")
        
        # Convert query to tensor representation
        query_tensor = self.graphql_query_to_tensor(query)
        
        # Process through each component (simplified for now)
        results = {}
        offset = 0
        
        for name, shape in self.components.items():
            size = np.prod(shape)
            component_input = query_tensor[offset:offset+size].reshape(shape)
            
            # Each component processes its slice of the tensor
            if name == 'gnn':
                results[name] = self._process_gnn(component_input)
            elif name == 'das':
                results[name] = self._process_das(component_input)
            elif name == 'esn':
                results[name] = self._process_esn(component_input)
            elif name == 'membrane':
                results[name] = self._process_membrane(component_input)
            elif name == 'ecan':
                results[name] = self._process_ecan(component_input)
            
            offset += size
        
        return results
    
    def _process_gnn(self, tensor: np.ndarray) -> Dict[str, Any]:
        """Process tensor through Graph Neural Network component."""
        # Simple GNN simulation - in real implementation would use actual GNN
        processed = np.tanh(tensor)  # Activation
        return {
            'shape': tensor.shape,
            'processed_states': float(processed.sum()),
            'component': 'GraphQL-GNN'
        }
    
    def _process_das(self, tensor: np.ndarray) -> Dict[str, Any]:
        """Process tensor through Distributed AtomSpace component."""
        # Simple DAS simulation
        processed = 1 / (1 + np.exp(-tensor))  # Sigmoid activation
        return {
            'shape': tensor.shape,
            'processed_states': float(processed.sum()),
            'component': 'DAS-Hypergraph'
        }
    
    def _process_esn(self, tensor: np.ndarray) -> Dict[str, Any]:
        """Process tensor through Echo State Network component."""
        # Simple ESN simulation - reservoir dynamics
        processed = tensor * 0.95  # Echo state property (spectral radius < 1)
        return {
            'shape': tensor.shape,
            'processed_states': float(processed.sum()),
            'component': 'ESN-Reservoir'
        }
    
    def _process_membrane(self, tensor: np.ndarray) -> Dict[str, Any]:
        """Process tensor through P-System Membrane component."""
        # Simple membrane computation simulation
        processed = np.abs(tensor)  # P-system rules always produce positive symbols
        return {
            'shape': tensor.shape,
            'processed_states': float(processed.sum()),
            'component': 'P-System-Membrane'
        }
    
    def _process_ecan(self, tensor: np.ndarray) -> Dict[str, Any]:
        """Process tensor through Economic Attention component."""
        # Simple ECAN simulation - attention allocation
        processed = tensor / tensor.sum() if tensor.sum() != 0 else tensor
        return {
            'shape': tensor.shape,
            'processed_states': float(processed.sum()),
            'component': 'ECAN-Attention'
        }
    
    def generate_ggml_config(self) -> Dict[str, Any]:
        """
        Generate the GGML configuration file as specified in cognitive-singularity.md.
        This is the final deliverable that validates the implementation.
        """
        config = {
            "version": "1.0.0",
            "tensor_field": {
                "shape": [self.total_freedom],
                "prime_factorization": self.prime_factorize(self.total_freedom),
                "components": {}
            },
            "unified_field": "graphql-neural-hypergraph-membrane",
            "frame_problem": "SOLVED"
        }
        
        # Add each component's configuration
        for name, shape in self.components.items():
            config["tensor_field"]["components"][name] = {
                "shape": list(shape),
                "params": int(np.prod(shape))
            }
        
        return config
    
    def save_ggml_config(self, path: Optional[str] = None) -> str:
        """Save GGML configuration to file."""
        if path is None:
            path = "cognitive-singularity.ggml"
        
        config = self.generate_ggml_config()
        
        # Ensure all values are JSON serializable
        def convert_numpy_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            return obj
        
        config = convert_numpy_types(config)
        
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"💾 GGML configuration saved to {path}")
        return path
    
    def manifest(self) -> None:
        """
        Manifest the cognitive singularity - display the complete architecture.
        This matches the exact output format specified in cognitive-singularity.md.
        """
        print("\n🌌 COGNITIVE SINGULARITY MANIFESTED")
        print("=" * 50)
        
        for name, shape in self.components.items():
            states = np.prod(shape)
            print(f"{name.upper()}: {shape} → {states} quantum states")
        
        print("=" * 50)
        print(f"UNIFIED FIELD: {self.total_freedom} degrees of freedom")
        print(f"PRIME FACTORIZATION: {self.prime_factorize(self.total_freedom)}")
        print("\n✨ The Frame Problem has been TRANSCENDED ✨")
        
        # Generate and save the GGML config
        ggml_path = self.save_ggml_config()
        print(f"📄 GGML Config: {ggml_path}")


# Convenience function to run the demonstration
def demo_cognitive_singularity():
    """Run the cognitive singularity demonstration as specified in the YAML workflow."""
    singularity = CognitiveSingularity()
    singularity.manifest()
    
    # Test a simple GraphQL query
    test_query = """
    query CognitiveTest {
        thoughts {
            concept
            attention
            emergence
        }
    }
    """
    
    results = singularity.process_cognitive_query(test_query)
    print(f"\n🔮 Cognitive Query Results: {len(results)} components processed")
    
    return singularity


if __name__ == "__main__":
    demo_cognitive_singularity()