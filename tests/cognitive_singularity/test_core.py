"""
Test suite for the Cognitive Singularity core implementation.
Validates all requirements from cognitive-singularity.md
"""

import pytest
import numpy as np
import json
import os
from pathlib import Path

# Import the module under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cognitive_singularity.core import CognitiveSingularity


class TestCognitiveSingularity:
    """Test the core CognitiveSingularity implementation."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.singularity = CognitiveSingularity()
    
    def test_component_tensor_shapes(self):
        """Test that component tensor shapes match specifications."""
        expected_shapes = {
            'gnn': (7, 7, 7),        # 343 states = 7³
            'das': (11, 5, 2),       # 110 states = 2 × 5 × 11
            'esn': (13, 3, 3),       # 117 states = 3² × 13
            'membrane': (5, 5, 5),   # 125 states = 5³
            'ecan': (3, 3, 3, 3)     # 81 states = 3⁴
        }
        
        assert self.singularity.components == expected_shapes
        
        # Verify individual component state counts
        assert np.prod(self.singularity.components['gnn']) == 343
        assert np.prod(self.singularity.components['das']) == 110
        assert np.prod(self.singularity.components['esn']) == 117
        assert np.prod(self.singularity.components['membrane']) == 125
        assert np.prod(self.singularity.components['ecan']) == 81
    
    def test_total_degrees_of_freedom(self):
        """Test that total degrees of freedom equals 776."""
        assert self.singularity.total_freedom == 776
        
        # Verify the calculation
        total = sum(np.prod(shape) for shape in self.singularity.components.values())
        assert total == 776
    
    def test_prime_factorization(self):
        """Test prime factorization of 776."""
        factors = self.singularity.prime_factorize(776)
        expected_factors = {2: 3, 97: 1}  # 2³ × 97 = 8 × 97 = 776
        
        assert factors == expected_factors
        
        # Verify the factorization is correct
        reconstructed = 1
        for prime, count in factors.items():
            reconstructed *= prime ** count
        assert reconstructed == 776
    
    def test_prime_factorization_edge_cases(self):
        """Test prime factorization with various inputs."""
        # Test prime numbers
        assert self.singularity.prime_factorize(97) == {97: 1}
        assert self.singularity.prime_factorize(2) == {2: 1}
        
        # Test composite numbers
        assert self.singularity.prime_factorize(8) == {2: 3}
        assert self.singularity.prime_factorize(12) == {2: 2, 3: 1}
        
        # Test 1
        assert self.singularity.prime_factorize(1) == {}
    
    def test_enumerate_all_states(self):
        """Test that all 776 states can be enumerated."""
        states = self.singularity.enumerate_all_states()
        
        # Should have exactly 776 states
        assert len(states) == 776
        
        # States should be unique integers from 0 to 776-1
        assert len(set(states)) == 776
        assert min(states) == 0
        assert max(states) == 775
    
    def test_tensor_field_generation(self):
        """Test tensor field generation for all components."""
        tensor_field = self.singularity.generate_tensor_field()
        
        # Should have all 5 components
        assert len(tensor_field) == 5
        assert set(tensor_field.keys()) == {'gnn', 'das', 'esn', 'membrane', 'ecan'}
        
        # Each tensor should have the correct shape
        for name, expected_shape in self.singularity.components.items():
            tensor = tensor_field[name]
            assert tensor.shape == expected_shape
            assert tensor.dtype == np.float32
            
            # Values should be small for numerical stability
            assert np.abs(tensor).max() < 1.0
    
    def test_attention_weights_calculation(self):
        """Test attention weight calculation."""
        attention = self.singularity.calculate_attention_weights()
        
        # Should have 5 weights (one per component)
        assert len(attention) == 5
        
        # Should be normalized (sum to 1.0)
        assert np.isclose(attention.sum(), 1.0)
        
        # All weights should be positive
        assert np.all(attention > 0)
        
        # GNN should have highest attention (most complex)
        gnn_attention = attention[0]  # GNN is first component
        assert gnn_attention == max(attention)
    
    def test_graphql_query_to_tensor(self):
        """Test GraphQL query encoding to tensor."""
        query1 = "query { user { name } }"
        query2 = "query { posts { title content } }"
        
        tensor1 = self.singularity.graphql_query_to_tensor(query1)
        tensor2 = self.singularity.graphql_query_to_tensor(query2)
        
        # Both tensors should have length 776
        assert len(tensor1) == 776
        assert len(tensor2) == 776
        
        # Different queries should produce different tensors
        assert not np.array_equal(tensor1, tensor2)
        
        # Same query should produce same tensor (deterministic)
        tensor1_repeat = self.singularity.graphql_query_to_tensor(query1)
        assert np.array_equal(tensor1, tensor1_repeat)
    
    def test_cognitive_query_processing(self):
        """Test full cognitive query processing pipeline."""
        test_query = """
        query CognitiveTest {
            thoughts {
                concept
                attention
                emergence
            }
        }
        """
        
        results = self.singularity.process_cognitive_query(test_query)
        
        # Should process all 5 components
        assert len(results) == 5
        expected_components = {'gnn', 'das', 'esn', 'membrane', 'ecan'}
        assert set(results.keys()) == expected_components
        
        # Each result should have expected structure
        for component, result in results.items():
            assert 'shape' in result
            assert 'processed_states' in result
            assert 'component' in result
            
            # Shape should match component specification
            expected_shape = self.singularity.components[component]
            assert result['shape'] == expected_shape
            
            # Processed states should be a number
            assert isinstance(result['processed_states'], (int, float))
    
    def test_ggml_config_generation(self):
        """Test GGML configuration generation."""
        config = self.singularity.generate_ggml_config()
        
        # Check required top-level fields
        assert config['version'] == '1.0.0'
        assert config['unified_field'] == 'graphql-neural-hypergraph-membrane'
        assert config['frame_problem'] == 'SOLVED'
        
        # Check tensor field structure
        tensor_field = config['tensor_field']
        assert tensor_field['shape'] == [776]
        assert tensor_field['prime_factorization'] == {2: 3, 97: 1}
        
        # Check components
        components = tensor_field['components']
        assert len(components) == 5
        
        for name, component_config in components.items():
            expected_shape = self.singularity.components[name]
            assert component_config['shape'] == list(expected_shape)
            assert component_config['params'] == np.prod(expected_shape)
    
    def test_ggml_config_save_and_load(self):
        """Test saving and loading GGML configuration."""
        # Save to temporary file
        temp_path = "test_cognitive.ggml"
        
        try:
            saved_path = self.singularity.save_ggml_config(temp_path)
            assert saved_path == temp_path
            assert os.path.exists(temp_path)
            
            # Load and verify content
            with open(temp_path, 'r') as f:
                loaded_config = json.load(f)
            
            expected_config = self.singularity.generate_ggml_config()
            assert loaded_config == expected_config
        
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_component_processing_methods(self):
        """Test individual component processing methods."""
        # Create test tensor for each component
        for name, shape in self.singularity.components.items():
            test_tensor = np.random.normal(0, 0.1, shape)
            
            if name == 'gnn':
                result = self.singularity._process_gnn(test_tensor)
            elif name == 'das':
                result = self.singularity._process_das(test_tensor)
            elif name == 'esn':
                result = self.singularity._process_esn(test_tensor)
            elif name == 'membrane':
                result = self.singularity._process_membrane(test_tensor)
            elif name == 'ecan':
                result = self.singularity._process_ecan(test_tensor)
            
            # All results should have consistent structure
            assert 'shape' in result
            assert 'processed_states' in result
            assert 'component' in result
            assert result['shape'] == shape
            assert isinstance(result['processed_states'], float)
    
    def test_manifest_method(self):
        """Test the manifest method (visual output)."""
        # This is mainly for coverage, as manifest() prints output
        # We'll capture stdout to verify it produces output
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            self.singularity.manifest()
        
        output = f.getvalue()
        
        # Should contain key phrases from the specification
        assert "COGNITIVE SINGULARITY MANIFESTED" in output
        assert "UNIFIED FIELD: 776 degrees of freedom" in output
        assert "Frame Problem has been TRANSCENDED" in output
        
        # Should list all components
        for component in self.singularity.components:
            assert component.upper() in output


class TestIntegration:
    """Integration tests for the full cognitive pipeline."""
    
    def test_full_cognitive_pipeline(self):
        """Test the complete cognitive processing pipeline."""
        # This is the exact test from cognitive-singularity.md
        singularity = CognitiveSingularity()
        states = singularity.enumerate_all_states()
        assert len(states) == 776
        
        # Verify prime factorization
        factors = singularity.prime_factorize(776)
        assert factors == {2: 3, 97: 1}
    
    def test_deployment_script_compatibility(self):
        """Test compatibility with the deployment script."""
        # Import deployment function directly 
        import sys
        from pathlib import Path
        script_path = Path(__file__).parent.parent.parent / "scripts"
        sys.path.insert(0, str(script_path))
        
        from deploy_singularity import deploy_cognitive_singularity
        
        # Should be able to deploy without errors
        singularity = deploy_cognitive_singularity(mode="bootstrap", validate=False)
        assert singularity is not None
        assert singularity.total_freedom == 776
    
    def test_ggml_output_validation(self):
        """Test that GGML output meets specification requirements."""
        singularity = CognitiveSingularity()
        config = singularity.generate_ggml_config()
        
        # Must match exact specification from cognitive-singularity.md
        expected_structure = {
            "version": "1.0.0",
            "tensor_field": {
                "shape": [776],
                "prime_factorization": {"2": 3, "97": 1},
                "components": {
                    "gnn": {"shape": [7, 7, 7], "params": 343},
                    "das": {"shape": [11, 5, 2], "params": 110},
                    "esn": {"shape": [13, 3, 3], "params": 117},
                    "membrane": {"shape": [5, 5, 5], "params": 125},
                    "ecan": {"shape": [3, 3, 3, 3], "params": 81}
                }
            },
            "unified_field": "graphql-neural-hypergraph-membrane",
            "frame_problem": "SOLVED"
        }
        
        # Convert to match string keys in expected structure
        config_str_keys = json.loads(json.dumps(config))
        assert config_str_keys == expected_structure