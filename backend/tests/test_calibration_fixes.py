"""
Test CLIP Calibration Fixes - Iteration 9
==========================================
Tests for:
1. POST /api/ai/calibration/log - lightweight logging (no file upload)
2. DELETE /api/ai/calibration/{id} - delete sample by ID
3. GET /api/ai/calibration - returns samples from calibration_log collection with _id field
4. Thresholds: 85% alta, 50% media, <50% rejeicao
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCalibrationLogEndpoint:
    """Tests for POST /api/ai/calibration/log - lightweight logging"""
    
    def test_log_correct_sample(self):
        """Test logging a correct calibration sample (is_correct=true)"""
        data = {
            "dish_clip": "test_frango_grelhado",
            "dish_real": "test_frango_grelhado",
            "is_correct": "true",
            "score": "0.87",
            "confidence": "alta",
            "source": "local_index"
        }
        response = requests.post(f"{BASE_URL}/api/ai/calibration/log", data=data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()
        assert result.get("ok") == True, f"Expected ok=true, got {result}"
        assert "id" in result, f"Expected 'id' in response, got {result}"
        assert result.get("message") == "Amostra registrada", f"Unexpected message: {result}"
        
        # Store ID for cleanup
        self.__class__.correct_sample_id = result.get("id")
        print(f"✓ Logged correct sample with ID: {self.__class__.correct_sample_id}")
    
    def test_log_incorrect_sample(self):
        """Test logging an incorrect calibration sample (is_correct=false)"""
        data = {
            "dish_clip": "test_arroz_branco",
            "dish_real": "test_arroz_integral",
            "is_correct": "false",
            "score": "0.65",
            "confidence": "media",
            "source": "local_index"
        }
        response = requests.post(f"{BASE_URL}/api/ai/calibration/log", data=data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()
        assert result.get("ok") == True, f"Expected ok=true, got {result}"
        assert "id" in result, f"Expected 'id' in response, got {result}"
        
        # Store ID for cleanup
        self.__class__.incorrect_sample_id = result.get("id")
        print(f"✓ Logged incorrect sample with ID: {self.__class__.incorrect_sample_id}")
    
    def test_log_sample_invalid_score(self):
        """Test that invalid score (0 or negative) is rejected"""
        data = {
            "dish_clip": "test_prato",
            "dish_real": "test_prato",
            "is_correct": "true",
            "score": "0",
            "confidence": "alta",
            "source": "local_index"
        }
        response = requests.post(f"{BASE_URL}/api/ai/calibration/log", data=data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        result = response.json()
        assert result.get("ok") == False, f"Expected ok=false for invalid score, got {result}"
        print("✓ Invalid score (0) correctly rejected")


class TestCalibrationGetEndpoint:
    """Tests for GET /api/ai/calibration - returns samples with _id field"""
    
    def test_get_calibration_returns_samples_with_id(self):
        """Test that GET /api/ai/calibration returns samples with _id field"""
        response = requests.get(f"{BASE_URL}/api/ai/calibration")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        result = response.json()
        assert result.get("ok") == True, f"Expected ok=true, got {result}"
        
        # Check structure
        assert "samples" in result, f"Expected 'samples' in response, got {result.keys()}"
        assert "stats" in result, f"Expected 'stats' in response, got {result.keys()}"
        assert "current_thresholds" in result, f"Expected 'current_thresholds' in response, got {result.keys()}"
        
        # Check samples have _id field
        samples = result.get("samples", [])
        if len(samples) > 0:
            sample = samples[0]
            assert "_id" in sample, f"Expected '_id' in sample, got {sample.keys()}"
            print(f"✓ GET /api/ai/calibration returns {len(samples)} samples with _id field")
        else:
            print("✓ GET /api/ai/calibration returns ok=true (no samples yet)")
    
    def test_thresholds_are_correct(self):
        """Test that thresholds are 85% alta, 50% media, <50% rejeicao"""
        response = requests.get(f"{BASE_URL}/api/ai/calibration")
        
        assert response.status_code == 200
        result = response.json()
        
        thresholds = result.get("current_thresholds", {})
        
        # Check threshold values
        alta = thresholds.get("alta", 0)
        media = thresholds.get("media", 0)
        rejeicao = thresholds.get("rejeicao", 0)
        
        assert alta == 0.85, f"Expected alta=0.85, got {alta}"
        assert media == 0.50, f"Expected media=0.50, got {media}"
        assert rejeicao == 0.50, f"Expected rejeicao=0.50, got {rejeicao}"
        
        print(f"✓ Thresholds correct: alta={alta*100}%, media={media*100}%, rejeicao=<{rejeicao*100}%")


class TestCalibrationDeleteEndpoint:
    """Tests for DELETE /api/ai/calibration/{id} - delete sample by ID"""
    
    def test_delete_sample_by_id(self):
        """Test deleting a calibration sample by ID"""
        # First create a sample to delete
        data = {
            "dish_clip": "test_delete_sample",
            "dish_real": "test_delete_sample",
            "is_correct": "true",
            "score": "0.75",
            "confidence": "media",
            "source": "test"
        }
        create_response = requests.post(f"{BASE_URL}/api/ai/calibration/log", data=data)
        assert create_response.status_code == 200
        sample_id = create_response.json().get("id")
        assert sample_id, "Failed to create sample for deletion test"
        print(f"  Created sample with ID: {sample_id}")
        
        # Now delete it
        delete_response = requests.delete(f"{BASE_URL}/api/ai/calibration/{sample_id}")
        
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        result = delete_response.json()
        assert result.get("ok") == True, f"Expected ok=true, got {result}"
        assert result.get("message") == "Amostra deletada", f"Unexpected message: {result}"
        print(f"✓ Successfully deleted sample {sample_id}")
    
    def test_delete_nonexistent_sample(self):
        """Test deleting a non-existent sample returns appropriate error"""
        fake_id = "000000000000000000000000"  # Valid ObjectId format but doesn't exist
        
        response = requests.delete(f"{BASE_URL}/api/ai/calibration/{fake_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        result = response.json()
        assert result.get("ok") == False, f"Expected ok=false for non-existent sample, got {result}"
        print("✓ Non-existent sample deletion correctly returns ok=false")
    
    def test_delete_invalid_id_format(self):
        """Test deleting with invalid ID format returns error"""
        invalid_id = "not-a-valid-objectid"
        
        response = requests.delete(f"{BASE_URL}/api/ai/calibration/{invalid_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        result = response.json()
        assert result.get("ok") == False, f"Expected ok=false for invalid ID, got {result}"
        print("✓ Invalid ID format correctly returns ok=false")


class TestCalibrationIntegration:
    """Integration tests for the full calibration flow"""
    
    def test_full_calibration_flow(self):
        """Test: Create sample -> Verify in GET -> Delete -> Verify removed"""
        # 1. Create a sample
        data = {
            "dish_clip": "test_integration_flow",
            "dish_real": "test_integration_flow",
            "is_correct": "true",
            "score": "0.92",
            "confidence": "alta",
            "source": "integration_test"
        }
        create_response = requests.post(f"{BASE_URL}/api/ai/calibration/log", data=data)
        assert create_response.status_code == 200
        sample_id = create_response.json().get("id")
        assert sample_id, "Failed to create sample"
        print(f"  1. Created sample: {sample_id}")
        
        # 2. Verify sample appears in GET
        get_response = requests.get(f"{BASE_URL}/api/ai/calibration")
        assert get_response.status_code == 200
        samples = get_response.json().get("samples", [])
        sample_ids = [s.get("_id") for s in samples]
        assert sample_id in sample_ids, f"Sample {sample_id} not found in GET response"
        print(f"  2. Verified sample in GET response")
        
        # 3. Delete the sample
        delete_response = requests.delete(f"{BASE_URL}/api/ai/calibration/{sample_id}")
        assert delete_response.status_code == 200
        assert delete_response.json().get("ok") == True
        print(f"  3. Deleted sample")
        
        # 4. Verify sample is removed
        get_response2 = requests.get(f"{BASE_URL}/api/ai/calibration")
        assert get_response2.status_code == 200
        samples2 = get_response2.json().get("samples", [])
        sample_ids2 = [s.get("_id") for s in samples2]
        assert sample_id not in sample_ids2, f"Sample {sample_id} still exists after deletion"
        print(f"  4. Verified sample removed from GET response")
        
        print("✓ Full calibration flow test passed")


class TestCleanup:
    """Cleanup test samples created during testing"""
    
    def test_cleanup_test_samples(self):
        """Clean up any test samples created during testing"""
        # Get all samples
        response = requests.get(f"{BASE_URL}/api/ai/calibration")
        if response.status_code != 200:
            print("  Could not get samples for cleanup")
            return
        
        samples = response.json().get("samples", [])
        test_samples = [s for s in samples if s.get("dish_clip", "").startswith("test_")]
        
        deleted_count = 0
        for sample in test_samples:
            sample_id = sample.get("_id")
            if sample_id:
                delete_response = requests.delete(f"{BASE_URL}/api/ai/calibration/{sample_id}")
                if delete_response.status_code == 200 and delete_response.json().get("ok"):
                    deleted_count += 1
        
        print(f"✓ Cleaned up {deleted_count} test samples")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
