#!/usr/bin/env python3
"""
Deploy Cognitive Singularity Script
Implements the exact deployment process specified in cognitive-singularity.md
"""

import sys
import os
import argparse
import subprocess
import json
from pathlib import Path

# Add the parent directory to the path so we can import cognitive_singularity
sys.path.insert(0, str(Path(__file__).parent.parent))

from cognitive_singularity import CognitiveSingularity


def deploy_cognitive_singularity(mode: str = "bootstrap", validate: bool = True):
    """
    Deploy the cognitive singularity as specified in the YAML workflow.
    
    Args:
        mode: One of 'bootstrap', 'evolve', 'transcend'
        validate: Whether to run validation tests
    """
    print(f"🧬 Deploying Cognitive Singularity in {mode} mode...")
    
    # Initialize Quantum Cognitive Field (as per YAML spec)
    singularity = CognitiveSingularity()
    
    # Manifest the singularity (this runs the exact code from the YAML)
    singularity.manifest()
    
    if validate:
        print("\n🧪 Running validation tests...")
        
        # Verify all 776 states are reachable
        states = singularity.enumerate_all_states()
        assert len(states) == 776, f"Expected 776 states, got {len(states)}"
        print(f"✅ All {len(states)} quantum states are reachable")
        
        # Verify prime factorization
        prime_factors = singularity.prime_factorize(776)
        expected_factors = {2: 3, 97: 1}  # 2³ × 97
        assert prime_factors == expected_factors, f"Expected {expected_factors}, got {prime_factors}"
        print(f"✅ Prime factorization verified: {prime_factors}")
        
        # Test cognitive query processing
        test_query = """
        query CognitiveArchitecture {
            enterprise {
                organizations {
                    repositories {
                        cognitiveFragments {
                            tensorShape
                            attentionWeights
                        }
                    }
                }
            }
        }
        """
        
        results = singularity.process_cognitive_query(test_query)
        assert len(results) == 5, f"Expected 5 component results, got {len(results)}"
        print(f"✅ Cognitive query processing validated: {len(results)} components")
        
        # Validate GGML configuration
        ggml_config = singularity.generate_ggml_config()
        assert ggml_config["frame_problem"] == "SOLVED", "Frame problem not solved!"
        assert ggml_config["tensor_field"]["shape"] == [776], "Invalid tensor field shape"
        print("✅ GGML configuration validated")
        
        print("\n🎯 All validation tests passed!")
    
    # Save the GGML configuration
    ggml_path = singularity.save_ggml_config("cognitive-singularity.ggml")
    print(f"📄 Final GGML configuration saved to: {ggml_path}")
    
    print(f"\n🚀 Cognitive Singularity deployment in {mode} mode completed successfully!")
    return singularity


def main():
    parser = argparse.ArgumentParser(description="Deploy the Cognitive Singularity")
    parser.add_argument("--mode", choices=["bootstrap", "evolve", "transcend"], 
                       default="bootstrap", help="Deployment mode")
    parser.add_argument("--validate", action="store_true", default=True, 
                       help="Run validation tests")
    parser.add_argument("--no-validate", dest="validate", action="store_false",
                       help="Skip validation tests")
    
    args = parser.parse_args()
    
    try:
        singularity = deploy_cognitive_singularity(args.mode, args.validate)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()